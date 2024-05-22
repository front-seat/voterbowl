import typing as t

from django.core.management.base import BaseCommand

from server.vb.models import Contest, School, Student
from server.vb.ops import enter_contest, send_validation_link_email


class Command(BaseCommand):
    """Force enter one or more students into a contest."""

    help = (
        "Force enter one or more students into a contest."
        "Students are identified by their email addresses or address patterns."
    )

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument("contest_id", type=int)
        parser.add_argument("emails", nargs="+", type=str)

    def handle(self, contest_id, emails: list[str], **options):
        """Handle the command."""
        contest = Contest.objects.get(pk=contest_id)
        school = contest.school
        for email in emails:
            self._process_students(contest, school, email)

    def _process_students(self, contest: Contest, school: School, email: str):
        """Enter one or more students into a contest, if not already entered."""
        if email[0] == "@":
            students = t.cast(
                t.Iterable[Student], school.students.filter(email__endswith=email[1:])
            )
        else:
            students = t.cast(t.Iterable[Student], school.students.filter(email=email))

        when = contest.start_at

        for student in students:
            if student.email.startswith("frontseat"):
                self.stdout.write(f"SKIPFRN {student.email}")
                continue
            contest_entry, entered = enter_contest(student, contest, when=when)
            winner = "!WINNER!" if contest_entry.is_winner else ""
            if entered:
                self.stdout.write(
                    f"ENTERED {student.email} ({contest_entry.roll}) {winner}"  # noqa
                )
                if contest_entry.is_winner:
                    link = send_validation_link_email(
                        student, student.email, contest_entry
                    )
                    self.stdout.write(f"\t--> email sent: {link.relative_url}")
            else:
                self.stdout.write(
                    f"ALREADY {student.email} ({contest_entry.roll}) {winner}"  # noqa
                )
