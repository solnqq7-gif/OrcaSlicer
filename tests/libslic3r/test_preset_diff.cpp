#include <catch2/catch_all.hpp>

#include <catch2/catch_test_macros.hpp>
#include <catch2/generators/catch_generators.hpp>
#include "libslic3r/Preset.hpp"
#include "libslic3r/PresetBundle.hpp"
#include "libslic3r/PrintConfig.hpp"

#include <algorithm>
#include <map>
#include <memory>
#include "libslic3r/Config.hpp"
#include <vector>
#include <cstddef>
#include <string>

using namespace Slic3r;

// Regression test for the python-plugin branch's intentional divergence from
// upstream in add_correct_opts_to_diff() (src/libslic3r/Preset.cpp): a vector
// option entry whose index is beyond the reference vector's length is reported
// dirty even when it duplicates an existing value. On main these duplicates
// were NOT flagged. See the comment on add_correct_opts_to_diff() in src/libslic3r/Preset.cpp.
TEST_CASE("deep_diff flags new vector entries that duplicate values[0]", "[PresetDiff][Config]")
{
    // reference: single-extruder vector (one entry)
    Preset reference(Preset::TYPE_PRINTER, "ref");
    reference.config.set_key_value("nozzle_diameter", new ConfigOptionFloats{0.4});

    // edited: a second extruder entry was added whose value duplicates the first
    Preset edited(Preset::TYPE_PRINTER, "edited");
    edited.config.set_key_value("nozzle_diameter", new ConfigOptionFloats{0.4, 0.4});

    // deep_compare = true routes through deep_diff() -> add_correct_opts_to_diff()
    std::vector<std::string> diff =
        PresetCollection::dirty_options(&edited, &reference, /*deep_compare=*/true);

    // The new index #1 is reported dirty even though 0.4 == values[0] (0.4).
    REQUIRE(std::find(diff.begin(), diff.end(), "nozzle_diameter#1") != diff.end());

    // Sanity: the unchanged existing index #0 is NOT reported, so the rule is
    // specific to new indices rather than flagging the whole vector.
    REQUIRE(std::find(diff.begin(), diff.end(), "nozzle_diameter#0") == diff.end());
}

TEST_CASE("deep_diff distinguishes absolute and percentage speeds for each variant", "[PresetDiff][Config]")
{
    const size_t changed_index = GENERATE(size_t(0), size_t(1));
    Preset reference(Preset::TYPE_PRINT, "ref");
    reference.config.set_key_value("small_perimeter_speed", new ConfigOptionFloatsOrPercents{{50., false}, {50., false}});

    Preset edited = reference;
    edited.config.option<ConfigOptionFloatsOrPercents>("small_perimeter_speed")->values[changed_index].percent = true;

    const auto diff = PresetCollection::dirty_options(&edited, &reference, /*deep_compare=*/true);
    REQUIRE(diff == std::vector<std::string>{"small_perimeter_speed#" + std::to_string(changed_index)});

    DynamicPrintConfig transferred = reference.config;
    transferred.apply_only(edited.config, diff);
    REQUIRE(*transferred.option("small_perimeter_speed") == *edited.config.option("small_perimeter_speed"));
}


TEST_CASE("Preset deltas preserve a disabled conditional wall toggle with a nonzero threshold", "[PresetDiff][ConditionalWallOrder]")
{
    const char *threshold = GENERATE("wall_sequence_overhang_angle", "wall_sequence_bottom_height");
    CAPTURE(threshold);
    PresetCollection presets(Preset::TYPE_PRINT, Preset::print_options(),
                             static_cast<const PrintRegionConfig &>(FullPrintConfig::defaults()));
    auto parent_config = DynamicPrintConfig::full_print_config();
    parent_config.set_key_value("inherits", new ConfigOptionString(""));
    const Preset parent = presets.load_preset("", "conditional_parent", parent_config, false);
    Preset child(Preset::TYPE_PRINT, "conditional_child");
    child.config = parent.config;
    child.config.set_key_value("inherits", new ConfigOptionString(parent.name));
    child.config.set_key_value(threshold, new ConfigOptionFloat(1.));
    child.config.set_key_value("enable_wall_sequence_overhang", new ConfigOptionBool(false));

    std::unique_ptr<Preset> delta(presets.get_preset_differed_for_save(child));
    REQUIRE(delta != nullptr);
    REQUIRE(delta->config.has("enable_wall_sequence_overhang"));
    delta->config.handle_legacy_composite();
    CHECK_FALSE(delta->config.opt_bool("enable_wall_sequence_overhang"));

    std::map<std::string, std::string> fields;
    REQUIRE(presets.get_differed_values_to_update(child, fields) == 0);
    REQUIRE(fields.count("enable_wall_sequence_overhang") == 1);
    CHECK(fields.at("enable_wall_sequence_overhang") == "0");
}

TEST_CASE("Legacy wall switching survives a project refresh from its system preset", "[PresetDiff][ConditionalWallOrder]")
{
    const char *threshold = GENERATE("wall_sequence_overhang_angle", "wall_sequence_bottom_height");
    CAPTURE(threshold);
    PresetCollection presets(Preset::TYPE_PRINT, Preset::print_options(),
                             static_cast<const PrintRegionConfig &>(FullPrintConfig::defaults()));
    DynamicPrintConfig system = presets.default_preset().config;
    REQUIRE_FALSE(system.opt_bool("enable_wall_sequence_overhang"));
    DynamicPrintConfig project = system;
    project.erase("enable_wall_sequence_overhang");
    project.set_key_value(threshold, new ConfigOptionFloat(1.));
    project.set_key_value("different_settings_to_system", new ConfigOptionStrings({
        escape_strings_cstyle({ threshold, "wall_loops" }), "filament_flow_ratio", "nozzle_diameter" }));
    project.handle_legacy_composite();
    const auto changes = project.option<ConfigOptionStrings>("different_settings_to_system")->values;
    const auto process_keys = PresetBundle::project_different_keys(changes.front());
    CHECK(process_keys.count(threshold) == 1);
    CHECK(process_keys.count("enable_wall_sequence_overhang") == 1);
    CHECK(changes.at(1) == "filament_flow_ratio");
    CHECK(changes.at(2) == "nozzle_diameter");

    const auto refreshed = Preset::load_external_config(Preset::TYPE_PRINT, system, project, process_keys,
        [&](const std::string &) { return &system; });
    CHECK(refreshed.opt_bool("enable_wall_sequence_overhang"));
    CHECK(refreshed.opt_float(threshold) == 1.);
    project.handle_legacy_composite();
    CHECK(project.option<ConfigOptionStrings>("different_settings_to_system")->values == changes);
}
