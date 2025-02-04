

# Класс data для хранения и аптейда данных пользователя
class Data:
    def __init__(self):
        self.user_pic_data = ''
        self.cloth_pic_data = ''
        self.dress_part_data = ''

    def update_data(self, user_pic_data='', cloth_pic_data='', dress_part_data=''):
        self.user_pic_data = user_pic_data
        self.cloth_pic_data = cloth_pic_data
        self.dress_part_data = dress_part_data

    def get_data(self):
        return self.user_pic_data, self.cloth_pic_data, self.dress_part_data



