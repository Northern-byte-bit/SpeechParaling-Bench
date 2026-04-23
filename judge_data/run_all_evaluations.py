import os
import subprocess

# List of all evaluation scripts to run
eval_scripts = [
    "judge_data/judge_code/dyn_var/dyn_var_ch.py",
    "judge_data/judge_code/dyn_var/dyn_var_en.py",
    "judge_data/judge_code/para_con/para_con_abstract_ch.py",
    "judge_data/judge_code/para_con/para_con_abstract_en.py",
    "judge_data/judge_code/para_con/para_con_long_multi_ch.py",
    "judge_data/judge_code/para_con/para_con_long_multi_en.py",
    "judge_data/judge_code/para_con/para_con_long_sin_ch.py",
    "judge_data/judge_code/para_con/para_con_long_sin_en.py",
    "judge_data/judge_code/para_con/para_con_short_multi_ch.py",
    "judge_data/judge_code/para_con/para_con_short_multi_en.py",
    "judge_data/judge_code/para_con/para_con_short_sin_ch.py",
    "judge_data/judge_code/para_con/para_con_short_sin_en.py",
    "judge_data/judge_code/sit_ada/sit_ada_multi_ch.py",
    "judge_data/judge_code/sit_ada/sit_ada_multi_en.py",
    "judge_data/judge_code/sit_ada/sit_ada_sin_ch.py",
    "judge_data/judge_code/sit_ada/sit_ada_sin_en.py",
]

def run_evaluations():
    print("Starting all evaluations...")
    for script in eval_scripts:
        if os.path.exists(script):
            print(f"\n>>> Running: {script}")
            try:
                subprocess.run(["python", script], check=True)
                print(f"Finished: {script}")
            except subprocess.CalledProcessError as e:
                print(f"Error running {script}: {e}")
        else:
            print(f"Script not found: {script}")
    print("\nAll evaluations completed.")

if __name__ == "__main__":
    run_evaluations()
