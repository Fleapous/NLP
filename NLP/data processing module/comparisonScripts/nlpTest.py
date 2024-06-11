import csv
import pandas as pd
import re


def normalize_value(value):
    value = value.lower()
    value = re.sub(r'[^a-z0-9]', '', value)
    return value


def compare_columns(processed_row, test_row):
    columns_to_check = [
        "<number_of_accidents_occured>",
        "<is_the_accident_data_yearly_monthly_or_daily>",
        "<day_of_the_week_of_the_accident>",
        "<exact_location_of_accident>",
        "<area_of_accident>",
        "<division_of_accident>",
        "<district_of_accident>",
        "<subdistrict_or_upazila_of_accident>",
        "<is_place_of_accident_highway_or_expressway_or_water_or_others>",
        "<is_country_bangladesh_or_other_country>",
        "<is_type_of_accident_road_accident_or_train_accident_or_waterways_accident_or_plane_accident>",
        "<total_number_of_people_killed>",
        "<total_number_of_people_injured>",
        "<is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>",
        "<primary_vehicle_involved>",
        "<secondary_vehicle_involved>",
        "<tertiary_vehicle_involved>",
        "<any_more_vehicles_involved>",
        "<available_ages_of_the_deceased>",
        "<accident_datetime_from_url>"
    ]

    row_data = {
        "title": processed_row.get("title", ""),
        "raw_text": processed_row.get("<raw_text>", "")
    }
    for column in columns_to_check:
        row_data[f"processed_{column}"] = processed_row.get(column, "")
        row_data[f"test_{column}"] = test_row.get(column, "")
    return row_data


def compare_rows(processed_rows, test_rows):
    row_data_list = []
    for _, processed_row in processed_rows:
        for _, test_row in test_rows:
            row_data = compare_columns(processed_row, test_row)
            row_data_list.append(row_data)
    return row_data_list


def find_row_by_title(processed_file, test_file, output_file):
    processed_df = pd.read_csv(processed_file, sep=';')
    test_df = pd.read_csv(test_file, sep=';')

    specific_file_name = "SuheybBecerek_TrifebiShinaSabrila_20240219_20221008_v2.csv"
    test_df = test_df[test_df['file_name'] == specific_file_name]

    test_df['title'] = test_df['<title>'].apply(lambda x: normalize_value(x.strip('<>')) if pd.notna(x) else x)
    processed_df['title'] = processed_df['<title>'].apply(normalize_value)
    totalErr = 0

    columns_to_check = [
        "<number_of_accidents_occured>",
        "<is_the_accident_data_yearly_monthly_or_daily>",
        "<day_of_the_week_of_the_accident>",
        "<exact_location_of_accident>",
        "<area_of_accident>",
        "<division_of_accident>",
        "<district_of_accident>",
        "<subdistrict_or_upazila_of_accident>",
        "<is_place_of_accident_highway_or_expressway_or_water_or_others>",
        "<is_country_bangladesh_or_other_country>",
        "<is_type_of_accident_road_accident_or_train_accident_or_waterways_accident_or_plane_accident>",
        "<total_number_of_people_killed>",
        "<total_number_of_people_injured>",
        "<is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>",
        "<primary_vehicle_involved>",
        "<secondary_vehicle_involved>",
        "<tertiary_vehicle_involved>",
        "<any_more_vehicles_involved>",
        "<available_ages_of_the_deceased>",
        "<accident_datetime_from_url>"
    ]

    headers = ["title", "raw_text"]
    for column in columns_to_check:
        headers.append(f"processed_{column}")
        headers.append(f"test_{column}")

    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    for test_title in test_df['title']:
        matching_processed_rows = processed_df[processed_df['title'] == test_title]
        matching_test_rows = test_df[test_df['title'] == test_title]

        if not matching_processed_rows.empty and not matching_test_rows.empty:
            row_data_list = compare_rows(matching_processed_rows.iterrows(), matching_test_rows.iterrows())
            with open(output_file, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                for row_data in row_data_list:
                    writer.writerow(row_data)
        else:
            totalErr += 1
            print(f"No matching row found for title: {test_title}")

    print(f"Total errors: {totalErr}")


if __name__ == "__main__":
    processed_file = 'processed_articles_final.csv'
    test_file = 'revised_annotations_as_of_May31st.csv'
    output_file = 'output_comparison.csv'
    find_row_by_title(processed_file, test_file, output_file)
