import json
from message import Message

class ChatHistory:
    """Чатын түүхийг удирдах класс"""
    
    def __init__(self, filename="chat_history.json"):
        """
        ChatHistory классын байгуулагч функц
        
        Parameters:
            filename (str): Чатын түүхийг хадгалах файлын нэр
        """
        self.filename = filename
        self.messages = []
        self.load_history()
    
    def add_message(self, message):
        """
        Шинэ мессеж нэмэх ба хадгалах
        
        Parameters:
            message (Message): Нэмэх мессеж
        """
        self.messages.append(message)
        self.save_history()
    
    def get_messages(self, count=None):
        """
        Сүүлийн мессежүүдийг авах
        
        Parameters:
            count (int, optional): Авах мессежийн тоо
        
        Returns:
            list: Мессежүүдийн жагсаалт
        """
        if count is None:
            return self.messages
        return self.messages[-count:]
    
    def load_history(self):
        """Файлаас чатын түүхийг ачаалах"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = [Message.from_dict(msg) for msg in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.messages = []
    
    def save_history(self):
        """Чатын түүхийг файлд хадгалах"""
        data = [msg.to_dict() for msg in self.messages]
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2) 