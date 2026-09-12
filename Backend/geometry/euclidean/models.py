from django.db import models


class SolvedProblem(models.Model):
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    question = models.TextField()
    geometry_type = models.CharField(max_length=80, blank=True)
    dimension = models.CharField(max_length=8, blank=True)
    operation = models.CharField(max_length=120)
    operation_label = models.CharField(max_length=160, blank=True)
    result = models.JSONField()
    explanation = models.JSONField()
    visualization = models.JSONField()
    response = models.JSONField()
    response_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["session_key", "response_hash"],
                name="unique_solved_problem_per_session_response",
            )
        ]

    def __str__(self):
        return f"{self.operation}: {self.question[:80]}"
