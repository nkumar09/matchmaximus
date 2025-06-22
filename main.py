#main.py
from workflows.profile_generation_workflow import run_profile_generation
from workflows.optimization_feedback_loop import run_feedback_analysis
from workflows.ab_testing_workflow import run_ab_test

if __name__ == '__main__':
    # To test generation: uncomment below
    run_profile_generation()

    # To test analytics: uncomment below
    run_feedback_analysis()

    # Uncomment to run A/B test
    # run_ab_test()