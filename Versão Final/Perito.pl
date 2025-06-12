%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% perito.pl (versao melhorada)
%% Sistema Pericial Interativo para Conteúdos de Streaming
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- dynamic executa/2.
:- dynamic resposta/2.
:- dynamic conhece/3.
:- dynamic nao_conhece/1.

perito :-
    write('Concha simples de Sistema Pericial'), nl,
    write('Versao de 2024'), nl, nl,
    esperaOrdens(123).

esperaOrdens(MC) :-
    mostraComandos(MC),
    write('> '),
    read(Comando),
    executa(MC,Comando).

mostraComandos(123) :-
    write('Comandos disponiveis (introduza o numero 1, 2 ou 3):'), nl,
    write('1 - Consultar uma Base de Conhecimento (BC)'), nl,
    write('2 - Solucionar'), nl,
    write('3 - Sair'), nl.

mostraComandos(23) :-
    write('Comandos disponiveis (introduza o numero 2 ou 3):'), nl,
    write('2 - Solucionar'), nl,
    write('3 - Sair'), nl.

executa(_,1) :-
    write('Nome da BC: '),
    read(F),
    consult(F),
    write('BC consultada com sucesso.'), nl, nl,
    continua.

executa(_,2) :-
    soluciona,
    esperaOrdens(23).

executa(_,3) :-
    nl,
    write('Volte Sempre!'), nl,
    write('Qualquer tecla para sair.'),
    get0(_),
    halt.

executa(MC,X) :-
    write(X),
    write(' nao e um comando valido!'), nl,
    esperaOrdens(MC).

continua :-
    retract( executa(_,1) :- _ ),
    esperaOrdens(23).

soluciona :-
    abolish(conhece,3),
    asserta(conhece(def,def,def)),
    objectivo(X),
    nl, nl, write('Resposta encontrada: '),
    write(X), nl, nl.

soluciona :-
    nl, nl, write('Nao foi encontrada resposta :-('), nl.

objectivo(Resultado) :-
    write('Pretende procurar por atributos (1) ou indicar um conteudo (2)?'), nl,
    read(Opcao),
    ( Opcao = 1 -> procurar_por_atributos(Resultado)
    ; Opcao = 2 -> procurar_por_titulo(Resultado)
    ).

% ---------------------------
% ATRIBUTOS
% ---------------------------

procurar_por_atributos(Titulo) :-
    questiona(tipo, Tipo, [tv, serie, filme, musica, podcast, ova]),
    ( Tipo == musica -> procurar_musica(Titulo)
    ; Tipo == podcast -> procurar_podcast(Titulo)
    ; procurar_outros(Tipo, Titulo)
    ).

procurar_musica(Titulo) :-
    questiona_genero(musica, Genero),
    write('Ano exato de lancamento (ex: 2022, ou null):'), nl,
    read(Ano),
    write('Valor minimo IMDb? (ex: 7.5, ou null):'), nl,
    read(IMDb),
    write('Nome do produtor (ou null):'), nl,
    read(Prod),
    write('Duracao maxima da musica (em minutos, ou null):'), nl,
    read(DuracaoMax),
    once((
        tipo(Titulo, musica),
        (Genero == null ; genero(Titulo, Genero)),
        (Ano == null ; ano(Titulo, Ano)),
        (Prod == null ; produtor(Titulo, Prod)),
        (number(IMDb) -> (classificacao_imdb(Titulo, N), N >= IMDb) ; true),
        (number(DuracaoMax) -> (duracao(Titulo, D), D =< DuracaoMax) ; true)
    )).

procurar_podcast(Titulo) :-
    write('Ano de lancamento (ou null):'), nl,
    read(Ano),
    write('Produtor (ou null):'), nl,
    read(Prod),
    write('Numero maximo de episodios (ou null):'), nl,
    read(EpsMax),
    once((
        tipo(Titulo, podcast),
        (Ano == null ; ano(Titulo, Ano)),
        (Prod == null ; produtor(Titulo, Prod)),
        (number(EpsMax) -> (episodios(Titulo, Eps), Eps =< EpsMax) ; true)
    )).

procurar_outros(Tipo, Titulo) :-
    questiona_genero(Tipo, Genero),
    write('Classificacao PEGI maxima (ou null):'), nl,
    read(Pegi),
    write('Ano de lancamento (ou null):'), nl,
    read(Ano),
    write('IMDb minimo (ou null):'), nl,
    read(IMDb),
    write('Max temporadas (ou null):'), nl,
    read(Temp),
    write('Max episodios (ou null):'), nl,
    read(Eps),
    write('Produtor (ou null):'), nl,
    read(Prod),
    write('Duracao max episodio (ou null):'), nl,
    read(Dur),
    once((
        tipo(Titulo, Tipo),
        (Genero == null ; genero(Titulo, Genero)),
        (Ano == null ; ano(Titulo, Ano)),
        (Prod == null ; produtor(Titulo, Prod)),
        (number(Pegi) -> (classificacao_pegi(Titulo, P), P =< Pegi) ; true),
        (number(IMDb) -> (classificacao_imdb(Titulo, I), I >= IMDb) ; true),
        (number(Temp) -> (temporadas(Titulo, T), T =< Temp) ; true),
        (number(Eps) -> (episodios(Titulo, E), E =< Eps) ; true),
        (number(Dur) -> (duracao(Titulo, D), D =< Dur) ; true)
    )).

% ---------------------------
% TITULO
% ---------------------------

procurar_por_titulo(Resultado) :-
    write('Sabe o nome completo do conteudo? (sim/nao)'), nl,
    read(Resp),
    (
        Resp == sim ->
            write('Qual o conteudo? (ex: dune)'), nl,
            read(Nome),
            plataforma_conteudo(Nome, Plataforma),
            Resultado = Plataforma
        ;
            procurar_por_titulo_parcial(Resultado)
    ).

procurar_por_titulo_parcial(Resultado) :-
    write('Parte do nome do conteudo?'), nl,
    read(SubNome),
    write('Tipo (tv, serie, filme, musica, podcast, ova, ou null):'), nl,
    read(Tipo),
    write('Ano (ou null):'), nl,
    read(Ano),
    write('Genero (ou null):'), nl,
    read(Genero),
    tipo(Titulo, TipoF), (Tipo == null ; Tipo == TipoF),
    atom_string(Titulo, NomeStr), sub_string(NomeStr, _, _, _, SubNome),
    (Ano == null ; ano(Titulo, Ano)),
    (Genero == null ; genero(Titulo, Genero)),
    plataforma_conteudo(Titulo, Plataforma),
    write('Titulo encontrado: '), write(Titulo), nl,
    Resultado = Plataforma.

% ---------------------------
% Perguntas base
% ---------------------------

questiona(Atributo,Valor) :- conhece(sim,Atributo,Valor).
questiona(Atributo,Valor) :- conhece(_,Atributo,Valor), !, fail.
questiona(Atributo,Valor) :- write(Atributo:Valor), write('? (sim/nao) '), read(R), processa(R,Atributo,Valor).

processa(sim,Atributo,Valor) :- asserta(conhece(sim,Atributo,Valor)).
processa(R,Atributo,Valor) :- asserta(conhece(R,Atributo,Valor)), !, fail.

questiona(Atr,Val,_) :- conhece(sim,Atr,Val).
questiona(Atr,_,_) :- conhece(sim,Atr,_), !, fail.
questiona(Atr,Val,ListaOpcoes) :-
    write('Qual o '), write(Atr), write('? '), nl,
    write(ListaOpcoes), nl,
    read(X),
    processa(X,Atr,Val,ListaOpcoes).

processa(Val,Atr,Val,_) :- asserta(conhece(sim,Atr,Val)).
processa(X,Atr,_,ListaOpcoes) :- member(X,ListaOpcoes), asserta(conhece(sim,Atr,X)), !, fail.
processa(X,Atr,Val,ListaOpcoes) :- write(X), write(' nao e valor aceite!'), nl, questiona(Atr,Val,ListaOpcoes).

questiona_genero(musica, Genero) :- questiona(genero, Genero, [pop, rock, jazz, classical, edm, funk, indie, folk, trap, hip_hop, metal, null]).
questiona_genero(podcast, Genero) :- questiona(genero, Genero, [comedia, true_crime, tecnologia, educacional, entrevistas, null]).
questiona_genero(serie, Genero) :- questiona(genero, Genero, [drama, comedia, fantasia, suspense, romance, null]).
questiona_genero(tv, Genero) :- questiona(genero, Genero, [anime, acao, comedia, drama, aventura, documentario, null]).
questiona_genero(filme, Genero) :- questiona(genero, Genero, [acao, aventura, comedia, drama, terror, ficcao, suspense, null]).
questiona_genero(ova, Genero) :- questiona(genero, Genero, [anime, acao, fantasia, null]).
questiona_genero(_, Genero) :- questiona(genero, Genero, [null]).