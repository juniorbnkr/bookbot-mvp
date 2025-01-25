def set_msgs(obj):
    return {
        'welcome': f'''Olá, {obj.name}. Seja bem vindo ao bookBot!''',
        'author_chosen': f'''
Escolha o autor do livro que deseja ler:
Digite 1 para *Machado de Assis*.
Digite 2 para *Graciliano Ramos*.
        ''',
        'book_chosed': f'''Muito bem! Aqui você selecionou o livro {obj.book_selected} \n''',
        'author_chosed': f'''O autor escolhido foi: {obj.author_chosed}.
Escolha o livro que deseja ler:
Digite 1 para *{obj.book_available[0]}*.
Ou digite 0 para voltar ao menu inicial.''',
        'wrong_author_chosed': f'''Autor inválido.''',
        'wrong_book_chosed': f'''Livro inválido.''',
        'next': f''' \n \n Digite: \n 1 para receber o capítulo seguinte \n 2 para ver o índice. \n \n ''',
        'invalid': f'''Opção inválida.''',        
    }

