def set_msgs(obj):
    return {
        'welcome': f'''Olá, {obj.name}. Seja bem vindo ao bookBot!''',
        'author_chosen': f'''
Escolha o autor do livro que deseja ler:
Digite 1 para *Machado de Assis*.
Digite 2 para *Graciliano Ramos*.
        ''',
        'book_chosed': f'''Muito bem! Você selecionou o livro {obj.book_selected} \n''',
        'author_chosed': f'''O autor escolhido foi: {obj.author_chosed_name}.
Escolha o livro que deseja ler:
Digite 1 para *{obj.book_available}*.
Ou digite 0 para voltar ao menu inicial.''',
        'wrong_author_chosed': f'''Autor inválido.''',
        'wrong_book_chosed': f'''Livro inválido.''',
        'next': f''' \n \n Digite: \n 1 para receber o capítulo seguinte \n 2 para ver o índice. \n \n ''',
        'invalid': f'''Opção inválida.''',  
        'start_or_continue': f'''Você parou no capítulo {obj.last_chap}.\n Digite 1 para continuar para o próximo capítulo. \n 
        Digite 2 para iniciar o livro novamente. \n \n ''',      
    }

