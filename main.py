#main.py
from workflows.profile_generation_workflow import run_profile_generation
from workflows.optimization_feedback_loop import run_feedback_analysis
from workflows.ab_testing_workflow import run_ab_test
from tools.network_utils import check_internet_connection

if __name__ == '__main__':
    if not check_internet_connection():
        print("🚫 No internet connection detected. Please connect to the internet and try again.")
        exit(1)
    # To test generation: uncomment below
    run_profile_generation()

    # To test analytics: uncomment below
    run_feedback_analysis()

    # Uncomment to run A/B test
    # run_ab_test()