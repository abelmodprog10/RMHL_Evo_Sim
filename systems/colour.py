import colorsys
import math

class Colour:
    def __init__(self, agent):
        self.agent = agent

    def get_rgb(self):
        """Get RGB values as tuple (r, g, b) with values 0-255"""
        hue = self.agent.genome.get_trait('colour')  # Stored as hue in [0.0, 1.0]
        saturation = 0.9
        value = 0.9
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_hex_color(self):
        """Get color as hex string for web display"""
        r, g, b = self.get_rgb()
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def average_hues(hues):
        """Averages hues (values from 0.0 to 1.0) correctly across the hue circle"""
        sin_sum = sum(math.sin(2 * math.pi * h) for h in hues)
        cos_sum = sum(math.cos(2 * math.pi * h) for h in hues)
        avg_angle = math.atan2(sin_sum, cos_sum)
        if avg_angle < 0:
            avg_angle += 2 * math.pi
        return avg_angle / (2 * math.pi)

    
    