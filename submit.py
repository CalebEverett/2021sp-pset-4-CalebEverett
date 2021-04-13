import os
from functools import partial
from typing import Dict, List

from canvasapi.quiz import QuizSubmissionQuestion
from csci_utils.canvas_utils import SubmissionManager
from git import Repo
from luigi import build, execution_summary

from pset_4 import Stylize

REPO = Repo(".")
CANVAS_URL = os.getenv("CANVAS_URL")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
SUCCESS = execution_summary.LuigiStatusCode.SUCCESS

stylize_kwargs = dict(
    bucket=os.getenv("BUCKET"),
    s3_image_path="pset_4/images/cat.jpg",
    local_image_path="pset_4/images/cat.jpg",
    local_output_path="pset_4/images/cat_mosaic.jpg",
    style_model="mosaic",
    docker_tag="new-style",
)

result = build([Stylize(**stylize_kwargs)], local_scheduler=True, detailed_summary=True)

# Question 1 - <p id="style">Upload a stylized image of your choice!</p>
# {'answer': None,
#  'answers': None,
#  'id': 2460829,
#  'question_type': 'file_upload_question'}

# Question 2 - <p id="hours">How many hours did you spend on this assignment?</p>
# {'answer': None,
#  'answers': [{'html': '', 'id': 8032, 'text': '15+'},
#              {'html': '', 'id': 3268, 'text': '0-5'},
#              {'html': '', 'id': 8610, 'text': '5-10'},
#              {'html': '', 'id': 568, 'text': '10-15'}],
#  'id': 2519518,
#  'question_type': 'multiple_choice_question'}

# Question 4 - <p id="commit">What is the commit id you are submitting from?</p>
# {'answer': None,
#  'answers': None,
#  'id': 2519519,
#  'question_type': 'short_answer_question'}

# Question 3 - <p id="clean">Is your git repo clean?</p>
# {'answer': None,
#  'answers': [{'id': 4031, 'text': 'True'}, {'id': 5153, 'text': 'False'}],
#  'id': 2519520,
#  'question_type': 'true_false_question'}


def answers_fn(questions: List[QuizSubmissionQuestion], file_id: int) -> List[Dict]:
    """Returns answers to Canvas quiz questions."""

    answers = [dict(id=q.id, answer=q.answer) for q in questions]

    # Question 1
    answers[0]["answer"] = file_id

    # Question 2
    answers[1]["answer"] = 568

    # Question 4
    answers[2]["answer"] = REPO.head.commit.hexsha[:8]

    # Question 3
    if REPO.is_dirty():
        answers[3]["answer"] = 5153
    else:
        answers[3]["answer"] = 4031

    return answers


if __name__ == "__main__":

    sm = SubmissionManager(
        assignment_name="Pset 4",
        quiz_name="Pset 4 Answers",
        min_quiz_score=0,
        canvas_url=CANVAS_URL,
        canvas_token=CANVAS_TOKEN,
    )

    sm.get_canvas_objects()
    assert result.status == SUCCESS
    file_id = sm.upload_quiz_file(stylize_kwargs["local_output_path"])

    sm.atomic_quiz_submit(partial(answers_fn, file_id=file_id), verbose=True)
    sm.assignment_submit(verbose=True, late_days=1)
