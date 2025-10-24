class Libro:
    def __init__(self, isbn: str, titulo: str, autor: str, editoral: str, fecha_publicacion: str):
        self.isbn = isbn.strip()
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.editorial = editoral.strip()
        self.fecha_publicacion = fecha_publicacion.strip()

    def to_dict(self):
        return {
            "Título": self.titulo,
            "Autor": self.autor,
            "Editorial": self.editorial,
            "Fecha de Publicación": self.fecha_publicacion
        }
    @classmethod
    def from_dict(cls, isbn: str, datos: dict):
        return cls(
            isbn=isbn,
            titulo=datos.get("Título", ""),
            autor=datos.get("Autor", ""),
            editorial=datos.get("Editorial", ""),
            fecha_publicacion=datos.get("Fecha de Publicación", "")
        )