from oscar.apps.dashboard.reports.utils import GeneratorRepository as CoreGeneratorRepository
from events.reports import TicketReportGenerator


class GeneratorRepository(CoreGeneratorRepository):

    def __init__(self):
        self.generators = [TicketReportGenerator] + self.generators
