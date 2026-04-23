import os
import subprocess

# Define the directory containing the calculation scripts
scripts_dir = "judge_data/score_calculate"

# Define the order of scripts to be executed
scripts_to_run = [
    "score_calculate_dyn_var.py", "score_calculate_para_con.py",
    "score_calculate_sit_ada.py", "calculate_final_scores.py"
]


def run_all_scripts():
    print(f"Starting execution of all scoring scripts in: {scripts_dir}\n")

    for script_name in scripts_to_run:
        script_path = os.path.join(scripts_dir, script_name)

        if not os.path.exists(script_path):
            print(f"Error: Script not found - {script_path}")
            continue

        print(f"--- Running: {script_name} ---")
        try:
            # Execute the script
            result = subprocess.run(["python", script_path],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            print(result.stdout)
            if result.stderr:
                print(f"Warnings/Errors from {script_name}:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running {script_name}:")
            print(e.stderr)
            # Stop execution if a critical script fails
            break

    print("\nAll scoring processes completed.")


if __name__ == "__main__":
    run_all_scripts()
