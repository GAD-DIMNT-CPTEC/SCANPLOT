# SCANPLOT

Este branch contém um redesign do SCANPLOT que exclui a necessidade de programação por parte do usuário. Trata-se de um desenvolvimento em estágio inicial, portanto há bugs e nem todas as funções podem funcionar.

Veja a discussão em https://github.com/GAM-DIMNT-CPTEC/SCANPLOT/discussions/30 para mais informações.

## Container Docker

Se você tiver o Docker instalado e configurado corretamente no seu computador, utilize os comandos a seguir para construir e executar o container com o SCANPLOT:

```
docker build -t scanplot .
docker run -p 5006:5006 scanplot
```

---

carlos.bastarz@inpe.br
