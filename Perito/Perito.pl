
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% perito.pl (corrigido)
%% Sistema Pericial Interativo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
    retract( executa(_,1) :- _ ), % Ja carregámos uma BC.
    esperaOrdens(23). % De futuro ja nao temos essa opcao.

%%%%%%%%%%%%%%%
% soluciona/0
%%%%%%%%%%%%%%%
soluciona :-
    abolish(conhece,3),
    asserta(conhece(def,def,def)), % apenas para o predicado
    objectivo(X), % conhece/3 estar definido...
    nl, nl, write('Resposta encontrada: '),
    write(X),
    nl, nl.

soluciona :-
    nl, nl, write('Nao foi encontrada resposta :-('), nl.

%%%%%%%%%%%%%%%
% questiona/2
%%%%%%%%%%%%%%%
questiona(Atributo,Valor) :-
    conhece(sim,Atributo,Valor).
questiona(Atributo,Valor) :-
    conhece(_,Atributo,Valor), !, fail.
questiona(Atributo,Valor) :-
    write(Atributo:Valor),
    write('? (sim/nao) '),
    read(R),
    processa(R,Atributo,Valor).

processa(sim,Atributo,Valor) :-
    asserta(conhece(sim,Atributo,Valor)).
processa(R,Atributo,Valor) :-
    asserta(conhece(R,Atributo,Valor)), !,
    fail.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% questiona/3 com lista de opcoes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
questiona(Atr,Val,_) :-
    conhece(sim,Atr,Val).
questiona(Atr,_,_) :-
    conhece(sim,Atr,_), !, fail.
questiona(Atr,Val,ListaOpcoes) :-
    write('Qual o valor para '),
    write(Atr),
    write('? '), nl,
    write(ListaOpcoes), nl,
    read(X),
    processa(X,Atr,Val,ListaOpcoes).

processa(Val,Atr,Val,_) :-
    asserta(conhece(sim,Atr,Val)).
processa(X,Atr,_,ListaOpcoes) :-
    member(X,ListaOpcoes),
    asserta(conhece(sim,Atr,X)), !, fail.
processa(X,Atr,Val,ListaOpcoes) :-
    write(X),
    write(' nao e valor aceite!'), nl,
    questiona(Atr,Val,ListaOpcoes).