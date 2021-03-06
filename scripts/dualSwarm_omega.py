from omega.games import gr1
from omega.games import enumeration as enum
from omega.symbolic import temporal as trl
from omega.games.enumeration import action_to_steps
from omega.symbolic import enumeration as sym_enum
import networkx as nx

import matplotlib.pyplot as plt

aut = trl.Automaton()
MAX_ROOMS = 2
aut.declare_variables(active=(1,MAX_ROOMS), 
                      home1 = (0,1), known_room1 = (0, MAX_ROOMS), pos1 = (0, MAX_ROOMS), known1 = (0,1),
                      home2 = (0,1), known_room2 = (0, MAX_ROOMS), pos2 = (0, MAX_ROOMS), known2 = (0,1),
                      turn = (1,3))
aut.varlist['env']=['active','turn']
aut.varlist['sys']=['known_room1','known1','pos1','home1','known_room2','known2','pos2','home2']
aut.prime_varlists()

specs = '''
    UNCHANGED_env == (active' = active)
    
    UNCHANGED_sys1 == 
    /\ home1' = home1
    /\ pos1' = pos1
    /\ known1' = known1
    /\ known_room1' = known_room1
    
    UNCHANGED_sys2 == 
    /\ home2' = home2
    /\ pos2' = pos2
    /\ known2' = known2
    /\ known_room2' = known_room2
    
    envInit == active = 1 /\ turn = 1
    
    sys1Init ==
    /\ pos1 = 0
    /\ home1 = 1
    /\ known_room1 = 0
    /\ known1 = 0
    
    sys2Init ==
    /\ pos2 = 0
    /\ home2 = 1
    /\ known_room2 = 0
    /\ known2 = 0
    
    envNext == 
    /\ (active \in 1..2 /\ active' \in 1..2)
    /\ (turn \in 1..3 /\ turn' \in 1..3)
    /\ (turn' != turn)
    /\ (turn = 1 => turn' = 2)
    /\ (turn = 2 => (turn' = 3 /\ UNCHANGED_env))
    /\ (turn = 3 => (turn' = 1 /\ UNCHANGED_env))

    sys1Step ==
    /\ (home1 = 1 => home1' = 0)
    /\ (~(home1 = 0 /\ known1' = 1) \/ home1' = 1)
    /\ (home1 = 1 <=> pos1 = 0)
    /\ (pos1' != pos1)
    /\ (~(home1 = 0 /\ pos1 = 1 /\ active = 1) \/ (known1' = 1 /\ known_room1' = 1))
    /\ (~(home1 = 0 /\ pos1 = 2 /\ active = 2) \/ (known1' = 1 /\ known_room1' = 2))
    /\ (~(home1 = 1 /\ known1 = 1 /\ known_room1 = 1) \/ (known1' = 1 /\ known_room1' = 1 /\ pos1' = 1))
    /\ (~(home1 = 1 /\ known1 = 1 /\ known_room1 = 2) \/ (known1' = 1 /\ known_room1' = 2 /\ pos1' = 2))
    /\ (~(home1 = 0 /\ (pos1 = 2 /\ active != 2)) \/ (known1' = 0 /\ known_room1' = 0 /\ pos1' = 1))
    /\ (~(home1 = 0 /\ (pos1 = 1 /\ active != 1)) \/ (known1' = 0 /\ known_room1' = 0 /\ pos1' = 2))

    sys1Next ==
    /\ (turn = 2 => sys1Step)
    /\ (turn != 2 => UNCHANGED_sys1)
    
    sys2Step == 
    /\ (home2 = 1 => home2' = 0)
    /\ (home2 = 1 <=> pos2 = 0)
    /\ (~(home2 = 0 /\ known2' = 1) \/ home2' = 1)
    /\ (pos2' != pos2)
    /\ (~(home2 = 0 /\ pos2 = 1 /\ active = 1) \/ (known2' = 1 /\ known_room2' = 1))
    /\ (~(home2 = 0 /\ pos2 = 2 /\ active = 2) \/ (known2' = 1 /\ known_room2' = 2))
    /\ (~(home2 = 1 /\ known2 = 1 /\ known_room2 = 1) \/ (known2' = 1 /\ known_room2' = 1 /\ pos2' = 1))
    /\ (~(home2 = 1 /\ known2 = 1 /\ known_room2 = 2) \/ (known2' = 1 /\ known_room2' = 2 /\ pos2' = 2))
    /\ (~(home2 = 0 /\ (pos2 = 2 /\ active != 2)) \/ (known2' = 0 /\ known_room2' = 0 /\ pos2' = 1))
    /\ (~(home2 = 0 /\ (pos2 = 1 /\ active != 1)) \/ (known2' = 0 /\ known_room2' = 0 /\ pos2' = 2))
  
    sys2Next ==
    /\ (turn = 3 => sys2Step)
    /\ (turn != 3 => UNCHANGED_sys2)

    environmentInit == envInit
    environmentNext == envNext
    sysInit == sys1Init /\ sys2Init
    sysNext == sys1Next /\ sys2Next
'''

aut.define(specs)
aut.init.update(
    env='envInit',
    sys='sysInit')
aut.action.update(
    env='envNext',
    sys='sysNext')
aut.win['<>[]'] = aut.bdds_from('turn = 1','turn=2','turn=3')
aut.win['[]<>'] = aut.bdds_from('TRUE')

aut.qinit = '\E \A'
aut.moore = True
aut.plus_one = True

z, yij, xijk = gr1.solve_streett_game(aut)
gr1.make_streett_transducer(z, yij, xijk, aut)
aut.varlist['sys'].append('_goal')
aut.prime_varlists()
# enumerate
g = enum.action_to_steps(aut, 'env', 'impl', qinit=aut.qinit)
h, _ = sym_enum._format_nx(g)
pd = nx.drawing.nx_pydot.to_pydot(h)
pd.write_pdf('dual_game_states_omega.pdf')