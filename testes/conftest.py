# Curso de francês: instância pessoal, fica fora do repositório público. Os testes que dependem dele são pulados lá.
import os
import pytest
from motor.especificacao import RAIZ

TEM_FRANCES = os.path.isdir(os.path.join(RAIZ, 'folhas', 'frances-delf-b1'))
requer_frances = pytest.mark.skipif(not TEM_FRANCES, reason='curso de francês fora deste repositório')
