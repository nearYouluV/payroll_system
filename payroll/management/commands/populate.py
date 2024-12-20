from django.core.management.base import BaseCommand
from payroll.models import Employee, PayoutRequest, CustomUser
from django.contrib.auth.models import Group
from random import randint, choice
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Populate the database with employees, users, and payout requests.'

    def handle(self, *args, **kwargs):
        positions = ["Software Engineer", "Designer", "Manager", "QA Specialist", "HR Specialist", "Accountant"]
        first_names = ["John", "Jane", "Alice", "Bob", "Eve", "Tom", "Anna", "Chris", "Mike", "Sophia"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Martinez", "Lee", "Wilson", "Taylor"]

        def calculate_available_earnings(hire_date, salary_rate):
            """
            Calculate available earnings for an employee based on their hire date and salary rate.
            """
            last_payout_date = hire_date + relativedelta(months=randint(2, 6))
            months_since_last_payout = (date.today().year - last_payout_date.year) * 12 + (date.today().month - last_payout_date.month)
            available_earnings = Decimal(months_since_last_payout) * salary_rate
            return max(available_earnings, 0), last_payout_date

        for i in range(10):
            # Generate random employee details
            first_name = choice(first_names)
            last_name = choice(last_names)
            position = choice(positions)
            salary_rate = Decimal(randint(50000, 120000)) / 100
            hire_date = date.today() - timedelta(days=randint(30, 365 * 5))

            available_earnings, last_payout_date = calculate_available_earnings(hire_date, salary_rate)

            # Create Employee
            employee = Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                position=position,
                salary_rate=salary_rate,
                hire_date=hire_date,
                available_earnings=available_earnings
            )

            # Create User Account
            password = 'Password123'
            user = CustomUser.objects.create_user(
                username=f'{first_name.lower()}_{last_name.lower()}_{position}_{i}',
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=f'{first_name.lower()}{last_name.lower()}@example.com'
            )
            user.employee = employee
            user.save()

            # Assign to Accountant group if position is Accountant
            if position == "Accountant":
                group, _ = Group.objects.get_or_create(name="Accountant")
                user.groups.add(group)

            # Create Payout Requests
            for _ in range(randint(1, 3)):
                min_amount = 1000
                max_amount = min(int(employee.available_earnings * 100), 50000)

                if max_amount < min_amount:
                    continue

                request_amount = Decimal(randint(min_amount, max_amount)) / 100
                payout_request = PayoutRequest.objects.create(
                    employee=employee,
                    amount=request_amount,
                    requested_at=now() - timedelta(days=randint(0, 30)),
                    status='Pending'
                )

                # Randomly decide to process the request
                if choice([True, False]):
                    if payout_request.amount <= employee.available_earnings:
                        employee.available_earnings -= payout_request.amount
                        employee.save()

                        payout_request.status = 'Processed'
                        payout_request.processed_at = now()
                        payout_request.save()

            self.stdout.write(f"Created Employee: {employee}, Available Earnings: {available_earnings} USD")
