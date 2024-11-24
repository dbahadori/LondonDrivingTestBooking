from abc import ABC, abstractmethod


class DataExtractor(ABC):
    @abstractmethod
    def extract_data(self) -> None:
        pass
