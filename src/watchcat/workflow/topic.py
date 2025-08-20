class Topic:
    def __init__(self, id: str, description: str) -> None:
        """A Topic with an ID and description.

        Args:
            id: Unique identifier for the topic.
            description: Description of the topic.
        """
        self.id = id
        self.description = description

    def to_serializable(self) -> dict:
        """Convert the Topic instance to a serializable dictionary.

        Returns:
            A dictionary representation of the Topic instance.
        """
        return {
            "id": self.id,
            "description": self.description
        }
        
    
    @classmethod
    def from_serializable(cls, data: dict) -> "Topic":
        """Create a Topic instance from a serializable dictionary.

        Args:
            data: A dictionary representation of a Topic.

        Returns:
            A Topic instance.
        """
        return cls(
            id=data["id"],
            description=data["description"]
        )
