import datetime

class Message:
    """Чатын мессежийг төлөөлөх класс"""
    
    def __init__(self, sender, content, timestamp=None):
        """
        Message классын байгуулагч функц
        
        Parameters:
            sender (str): Мессеж илгээгчийн нэр
            content (str): Мессежийн агуулга
            timestamp (datetime, optional): Мессеж илгээгдсэн хугацаа
        """
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now()
    
    def __str__(self):
        """Message объектыг текст хэлбэрт хөрвүүлэх"""
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.sender}: {self.content}"
    
    def to_dict(self):
        """Message объектыг dictionary хэлбэрт хөрвүүлэх"""
        return {
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def from_dict(cls, data):
        """Dictionary-гээс Message объект үүсгэх"""
        timestamp = datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        return cls(data['sender'], data['content'], timestamp) 