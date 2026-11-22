import unittest

from src.validaciones import validar_contrasena


class PruebasPoliticaContrasenas(unittest.TestCase):
    def test_rechaza_claves_debiles(self):
        claves = ("123456", "123456789012", "Abcdefghi1!", "abcdefghijkl!4",
                  "ABCDEFGHIJKL!4", "Abcdefghijkl!", "Abcdefghijkl4", "Abcdefghijk4 ",
                  "Password123!", "Noticiero123!", "ClaveConSalto1!\n", "A" * 125 + "a1!x")
        for clave in claves:
            with self.subTest(clave=clave), self.assertRaises(ValueError):
                validar_contrasena(clave)

    def test_acepta_combinaciones_y_frases_largas(self):
        for clave in ("BosqueAzul!73", "Una frase larga 82!", "ÁrbolesVerdes!52", "A" * 125 + "a1!"):
            with self.subTest(clave=clave):
                validar_contrasena(clave)

    def test_rechaza_valores_no_textuales(self):
        for clave in (None, 123456, b"BosqueAzul!73"):
            with self.subTest(tipo=type(clave)), self.assertRaises(ValueError):
                validar_contrasena(clave)
