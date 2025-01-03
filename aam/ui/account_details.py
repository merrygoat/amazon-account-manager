import datetime
from typing import TYPE_CHECKING

import nicegui.events
from nicegui import ui

import aam.utilities
from aam.models import Account, Person, Sysadmin

if TYPE_CHECKING:
    from aam.main import UIMainForm


class UIAccountDetails:
    def __init__(self, parent: "UIMainForm"):
        self.parent = parent

        ui.html("Account Details").classes("text-2xl")
        with ui.grid(columns='auto 1fr').classes('w-full'):
            ui.label("Name:")
            self.account_name = ui.label("")
            ui.label("Account ID:")
            self.account_id = ui.label("")
            ui.label("Root Email:")
            self.root_email = ui.label("")
            ui.label("Account Status:")
            self.account_status = ui.label("")
            ui.html("Billing/Contact Details").classes("text-2xl")
            ui.element()
            ui.label("Budget Holder:")
            self.budget_holder = ui.select([], on_change=self.update_budget_holder_email).props("clearable")
            ui.label("Budget Holder email:")
            self.budget_holder_email = ui.label("")
            ui.label("Finance Code:")
            self.finance_code = ui.input().props("clearable")
            ui.label("Task Code:")
            self.task_code = ui.input().props("clearable")
            ui.label("Sysadmin:")
            self.sysadmin = ui.select([], on_change=self.update_sysadmin_email).props("clearable")
            ui.label("Sysadmin email:")
            self.sysadmin_email = ui.label("")
            ui.label("Creation date")
            self.account_creation_input = aam.utilities.date_picker()
            ui.label("Closure date")
            self.account_closure_input = aam.utilities.date_picker()
        with ui.column().classes("items-end w-full"):
            self.save_changes = ui.button("Save Changes", on_click=self.save_account_changes)

        self.budget_holder.disable()
        self.sysadmin.disable()
        self.finance_code.disable()
        self.task_code.disable()
        self.save_changes.disable()

    def save_account_changes(self):
        account: Account = Account.get(Account.id == self.account_id.text)

        account_creation_date = self.account_creation_input.value
        if account_creation_date:
            try:
                account_creation_date = datetime.date.fromisoformat(account_creation_date)
            except ValueError as e:
                ui.notify(f"Account creation date is not valid: {e.args[0]}")
                return 0
            else:
                account.creation_date = account_creation_date

        account_closure_date = self.account_closure_input.value
        if account_closure_date:
            try:
                account_closure_date = datetime.date.fromisoformat(account_closure_date)
            except ValueError as e:
                ui.notify(f"Account closure date is not valid: {e.args[0]}")
            else:
                account.closure_date = account_closure_date

        selected_sysadmin = self.sysadmin.value
        if selected_sysadmin:
            selected_sysadmin = Person.get(Person.id == selected_sysadmin)
            Sysadmin.create(person=selected_sysadmin, account=account)
        else:
            sysadmin = Sysadmin.get(Sysadmin.account == account.id)
            sysadmin.delete_instance()
        selected_budget_holder = self.budget_holder.value
        if selected_budget_holder:
            selected_budget_holder = Person.get(Person.id == selected_budget_holder)
            account.budget_holder = selected_budget_holder
        else:
            account.budget_holder = None
        ui.notify("Record updated.")
        account.finance_code = self.finance_code.value
        account.task_code = self.task_code.value

        account.save()
        self.parent.bills.update_bill_grid()

    def update_sysadmin_email(self, event: nicegui.events.ValueChangeEventArguments):
        selected_person = event.sender.value
        if selected_person:
            person = Person.get(id=selected_person)
            self.sysadmin_email.set_text(person.email)
        else:
            self.sysadmin_email.set_text("")

    def update_budget_holder_email(self, event: nicegui.events.ValueChangeEventArguments):
        selected_person = event.sender.value
        if selected_person:
            person = Person.get(id=selected_person)
            self.budget_holder_email.set_text(person.email)
        else:
            self.budget_holder_email.set_text("")

    def clear(self):
        self.account_name.set_text("")
        self.account_id.set_text("")
        self.root_email.set_text("")
        self.account_status.set_text("")
        self.budget_holder.set_value(None)
        self.budget_holder_email.set_text("")
        self.finance_code.set_value(None)
        self.task_code.set_value(None)
        self.sysadmin.set_value(None)
        self.sysadmin_email.set_text("")
        self.finance_code.disable()
        self.task_code.disable()
        self.budget_holder.disable()
        self.sysadmin.disable()
        self.save_changes.disable()
        self.parent.notes.clear()

    def update(self, account: Account | None):
        if account is None:
            self.clear()
            return 0

        self.sysadmin.enable()
        self.budget_holder.enable()
        self.finance_code.enable()
        self.task_code.enable()
        self.save_changes.enable()

        self.account_name.set_text(account.name)
        self.account_id.set_text(account.id)
        self.root_email.set_text(account.email)
        self.account_status.set_text(account.status)

        all_people = {person.id: person.full_name for person in Person.select()}
        self.budget_holder.set_options(all_people)
        self.sysadmin.set_options(all_people)

        self.finance_code.set_value(account.finance_code)
        self.task_code.set_value(account.task_code)

        if account.budget_holder:
            self.budget_holder.set_value(account.budget_holder.id)
        else:
            self.budget_holder.set_value(None)

        sysadmin = Sysadmin.get_or_none(Sysadmin.account == account.id)
        if sysadmin:
            self.sysadmin.set_value(sysadmin.person.id)
        else:
            self.sysadmin.set_value(None)

        if account.creation_date:
            self.account_creation_input.value = account.creation_date.isoformat()
        else:
            self.account_creation_input.value = ""

        if account.closure_date:
            self.account_closure_input.value = account.closure_date.isoformat()
        else:
            self.account_closure_input.value = ""
