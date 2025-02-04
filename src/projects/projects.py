from src.projects.base_project import BaseProject

class GeosProject(BaseProject):
    def __init__(self):
        super().__init__(
            name="ГЕОС",
            tg_link="https://t.me/geos_project",
            description="ГЕОС - это инновационный проект, направленный на ... .",
            folder_presentation_name="geos",
        )

class FarmProject(BaseProject):
    def __init__(self):
        super().__init__(
            name="Ферма",
            tg_link="https://t.me/farm_project",
            description="Ферма - это передовой агротехнологический проект, который ...",
            folder_presentation_name="farm",
        )
