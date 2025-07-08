import math
import random

class VisionSystem:
    """
    Efficient vision system for agents with binocular depth perception.
    Updates every 3 steps for performance.
    """
    
    def __init__(self, n_eyes=2, eye_fov=60, max_vision_range=100):
        self.n_eyes = n_eyes
        self.eye_fov = math.radians(eye_fov)  # Convert to radians
        self.max_vision_range = max_vision_range
        
    def update_agent_vision(self, agent):
        """Update agent's vision if it's time (every 3 steps)"""
        if not hasattr(agent, 'vision_step_counter'):
            agent.vision_step_counter = 0
            agent.visible_entities = []
            
        agent.vision_step_counter += 1
        
        if agent.vision_step_counter >= 3:
            agent.vision_step_counter = 0
            agent.visible_entities = self.get_visible_entities(agent)
            
    def get_visible_entities(self, agent):
        """Get all entities visible to the agent"""
        if not agent.world:
            return []
            
        # Get all entities within max vision range using spatial hash
        nearby_entities = agent.world.get_entities_in_radius(
            agent.x, agent.y, self.max_vision_range
        )
        
        # Remove self from candidates
        nearby_entities = [e for e in nearby_entities if e != agent]
        
        visible_entities = []
        eye_positions = self._get_eye_positions(agent)
        
        for entity in nearby_entities:
            # Calculate relative position
            dx = entity.x - agent.x
            dy = entity.y - agent.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > self.max_vision_range:
                continue
                
            # Calculate angle relative to agent's facing direction
            entity_angle = math.atan2(dy, dx)
            relative_angle = self._normalize_angle(entity_angle - agent.angle)
            
            # Check which eyes can see this entity
            seeing_eyes = []
            for eye_idx, eye_angle in enumerate(eye_positions):
                if self._is_in_fov(relative_angle, eye_angle, self.eye_fov):
                    seeing_eyes.append(eye_idx)
                    
            if seeing_eyes:
                # Entity is visible to at least one eye
                binocular_vision = len(seeing_eyes) == 2
                
                # Apply depth perception noise
                perceived_distance = self._apply_depth_noise(
                    distance, binocular_vision
                )
                
                visible_entities.append({
                    'entity': entity,
                    'distance': perceived_distance,
                    'true_distance': distance,  # For debugging
                    'angle': relative_angle,
                    'type': getattr(entity, 'type', 'Unknown'),
                    'binocular': binocular_vision,
                    'seeing_eyes': seeing_eyes
                })
                
        return visible_entities
    
    def _get_eye_positions(self, agent):
        """Get eye positions based on eye_pos trait"""
        eye_pos = agent.genome.get_trait('eye_pos')
        
        if self.n_eyes == 2:
            # Calculate eye angles based on eye_pos
            # 0.0 = both eyes forward (0°, 0°)
            # 0.5 = eyes on sides (-90°, 90°)  
            # 1.0 = eyes backward (-180°, 180°)
            
            # Linear interpolation from 0 to π radians (0° to 180°)
            max_angle = eye_pos * math.pi
            
            eye1_angle = -max_angle  # Left eye
            eye2_angle = max_angle   # Right eye
                
            return [eye1_angle, eye2_angle]
        else:
            # For future expansion - distribute eyes evenly
            eye_angles = []
            for i in range(self.n_eyes):
                angle = (2 * math.pi * i) / self.n_eyes
                eye_angles.append(angle)
            return eye_angles
    
    def _is_in_fov(self, entity_angle, eye_angle, fov):
        """Check if entity is within eye's field of view"""
        # Calculate the difference between entity angle and eye angle
        angle_diff = self._normalize_angle(entity_angle - eye_angle)
        return abs(angle_diff) <= fov / 2
    
    def _normalize_angle(self, angle):
        """Normalize angle to [-π, π]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    def _apply_depth_noise(self, true_distance, binocular_vision):
        """Apply biologically-inspired depth perception noise"""
        # Base error rates
        base_error = 0.02 if binocular_vision else 0.08  # 2% vs 8%
        
        # Distance scaling factor
        distance_factor = 1 + (true_distance / self.max_vision_range)
        
        # Calculate error magnitude
        error_magnitude = base_error * distance_factor
        
        # Apply random noise
        noise = random.uniform(-error_magnitude, error_magnitude)
        perceived_distance = true_distance * (1 + noise)
        
        # Ensure distance is positive
        return max(0.1, perceived_distance)
    
    def get_vision_data_for_nn(self, agent):
        """
        Format vision data for neural network input.
        Returns normalized vectors ready for NN processing.
        """
        if not hasattr(agent, 'visible_entities'):
            return {'distances': [], 'angles': [], 'types': []}
            
        distances = []
        angles = []
        types = []
        
        for entity_data in agent.visible_entities:
            # Normalize distance (0 = very close, 1 = max range)
            norm_distance = min(1.0, entity_data['distance'] / self.max_vision_range)
            distances.append(norm_distance)
            
            # Normalize angle (-1 = left, 0 = forward, 1 = right)
            norm_angle = entity_data['angle'] / math.pi
            angles.append(norm_angle)
            
            # One-hot encode types
            entity_type = entity_data['type']
            type_vector = [0, 0, 0]  # [prey, predator, plant]
            if entity_type == 'Prey':
                type_vector[0] = 1
            elif entity_type == 'Predator':
                type_vector[1] = 1
            elif entity_type == 'Plant':
                type_vector[2] = 1
            types.append(type_vector)
            
        return {
            'distances': distances,
            'angles': angles,
            'types': types,
            'binocular': [e['binocular'] for e in agent.visible_entities]
        }


# Global vision system instance
vision_system = VisionSystem()

def update_agent_vision(agent):
    """Convenience function to update agent vision"""
    vision_system.update_agent_vision(agent)

def get_vision_data_for_nn(agent):
    """Convenience function to get NN-ready vision data"""
    return vision_system.get_vision_data_for_nn(agent)