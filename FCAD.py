import threading


#Computes the lexicographic tree of the union-closed family F generated by B
def tree(B):
    F = [set()]
    gamma = [[]]
    for b in B:
        indice = 0
        while indice < len(F):
            f = F[indice]
            fp = f.union(b)
            if fp not in F:
                F.append(fp)
                gamma.append([])
            if b not in gamma[F.index(fp)]:
                gamma[F.index(fp)].append(b)
            indice += 1
    return F,gamma

def factual_distance(C1,C2,p):
    intersect = []
    for X in C1[0]:
        if X in C2[0]:
            intersect.append(X)
    return pow(pow(len(C1[0])-len(intersect),p)+pow(len(C2[0])-len(intersect),p),1.0/p)/(len(intersect)+pow(pow(len(C1[0])-len(intersect),p)+pow(len(C2[0])-len(intersect),p),1.0/p))


def conceptual_distance(L1,L2,p,q):
    nbTrucs = []
    Extents = [X[0] for X in L1]        
    nbTrucs.append(max([len(E) for E in Extents]))
    Intents = [X[1] for X in L1]        
    nbTrucs.append(max([len(I) for I in Intents]))
    EI1=[[E for [E,_] in L1],[I for [_,I] in L1]]
    EI2=[[E for [E,_] in L2],[I for [_,I] in L2]]
    R = [0,0]
    for sens in range(2):
        distances = 0
        for elem in range(nbTrucs[sens]):
            #trouver les introducteurs d'elem
            Sets1 = sorted(zip(EI1[0],EI1[1]), key=lambda pair: pair[sens])
            Intro1 = []
            for X in Sets1:
                if elem in X[sens]:
                    Intro1 = X[abs(sens-1)]
                    break
            Sets2 = sorted(zip(EI2[0],EI2[1]), key=lambda pair: pair[sens])
            Intro2 = []
            for X in Sets2:
                if elem in X[sens]:
                    Intro2 = X[abs(sens-1)]
                    break
            #calculer la distance entre les ensembles d'objets/attributes ayant elem dans leur dérivation
            nb1 = pow(2,len(Intro1))
            nb2 = pow(2,len(Intro2))
            nb12 = pow(2,len(set(Intro1).intersection(set(Intro2))))
            distance = pow(pow(abs(nb1-nb12),q)+pow(abs(nb2-nb12),q),1.0/q)
            if distance != 0:
                distance = distance/(nb12+distance)
            distances += pow(distance,p)
        R[sens] = pow(distances,1.0/p)/(pow(nbTrucs[sens],1.0/p))
    return min(R)

def logical_distance(I1,I2,nbAtt,p,q):
    somm = 0
    threads = []
    results = []
    for a in range(nbAtt):
        t = threading.Thread(target=logical_ter, args=(I1,I2,nbAtt,q,a,results))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()  
    som = 0
    for x in results:
        som += pow(x,p)
    return pow(som,1.0/p)/(pow(nbAtt,1.0/p))   

def logical_ter(Imps1,Imps2,nbAtt,q,a,result):   
    premisses_de_a_1 = []
    premisses_de_a_2 = []
    for [A,B] in Imps1:
        if a in B:
            premisses_de_a_1.append(A)
    for [A,B] in Imps2:
        if a in B:
            premisses_de_a_2.append(A)
        
    if not(len(premisses_de_a_1) == 1 and premisses_de_a_1[0] == set()):
        premisses_de_a_1.append(set([a]))
    if not(len(premisses_de_a_2) == 1 and premisses_de_a_2[0] == set()):
        premisses_de_a_2.append(set([a]))


    #calculer les intersections des premisses
    intersections_premisses = []
    for A in premisses_de_a_1:
        for B in premisses_de_a_2:
            I = set(A).union(set(B))
            if I not in intersections_premisses:
                intersections_premisses.append(I)
    aVirer = []
    for I in intersections_premisses:
        virer = False
        for I2 in intersections_premisses:
            if I2.issubset(I) and len(I) != len(I2):
                virer = True
                break
        if virer:
            aVirer.append(I)
    for I in aVirer:
        intersections_premisses.remove(I)
    if len(premisses_de_a_1) == 0 and len(premisses_de_a_2) != 0:
        intersections_premisses = premisses_de_a_1
    if len(premisses_de_a_2) == 0 and len(premisses_de_a_1) != 0:
        intersections_premisses = premisses_de_a_2

    premisses_L1 = premisses_de_a_1
    premisses_L2 = premisses_de_a_2


    #Dedekind-Macneille completion des premisses
    if len(intersections_premisses) > 0:
        Comp1,_ = tree(intersections_premisses)
    else:
        Comp1 = []
    if len(premisses_L1) > 0:
        CompL1,_ = tree(premisses_L1)
    else:
        CompL1 = []
    if len(premisses_L2) > 0:
        CompL2,_ = tree(premisses_L2)
    else:
        CompL2 = []


    class Concept:
        def __init__(self, c, b, t):
            self.c = c
            self.b = b
            self.t = t
    #Calcul pour les intersections
    classe_max_intersection = 0
    dict = {}
    CL2 = [Concept(X,0,0) for X in Comp1]
    #creation du dictionnaire
    for i in range(len(CL2)):
        dict[i] = []
        for conc in CL2:
            if set(CL2[i].c).issubset(conc.c) and not set(conc.c).issubset(CL2[i].c):
                dict[i].append(conc)
    #Calcul des classes d'équivalences
    Indices = sorted(zip(CL2,range(len(CL2))), key=lambda pair: pair[0].c)
    end = 0
    while end == 0:
        end = 1
        for i in Indices:
            if CL2[i[1]].b == 0:
                aTraiter = 1
                sum = 0
                for conc2 in dict[i[1]]:
                    if conc2.b == 0:
                        aTraiter = 0
                        break
                    sum += conc2.t
                if aTraiter == 1 and (len(CL2[i[1]].c) > 0 or len(CL2) == 1):
                    end = 0
                    CL2[i[1]].t = pow(2,(nbAtt-len(CL2[i[1]].c)))-sum
                    classe_max_intersection += CL2[i[1]].t
                    CL2[i[1]].b = 1


    #Calcul pour L1
    classe_max_L1 = 0
    dict = {}
    CL2 = [Concept(X,0,0) for X in CompL1]
    #creation du dictionnaire 
    for i in range(len(CL2)):
        dict[i] = []
        for conc in CL2:
            if set(CL2[i].c).issubset(conc.c) and not set(conc.c).issubset(CL2[i].c):
                dict[i].append(conc)
    #Calcul des classes d'équivalences
    Indices = sorted(zip(CL2,range(len(CL2))), key=lambda pair: pair[0].c)
    end = 0
    while end == 0:
        end = 1
        for i in Indices:
            if CL2[i[1]].b == 0:
                aTraiter = 1
                sum = 0
                for conc2 in dict[i[1]]:
                    if conc2.b == 0:
                        aTraiter = 0
                        break
                    sum += conc2.t
                if aTraiter == 1 and (len(CL2[i[1]].c) > 0 or len(CL2) == 1):
                    end = 0
                    CL2[i[1]].t = pow(2,(nbAtt-len(CL2[i[1]].c)))-sum
                    classe_max_L1 += CL2[i[1]].t
                    CL2[i[1]].b = 1
    #Calcul pour L2
    classe_max_L2 = 0
    dict = {}
    CL2 = [Concept(X,0,0) for X in CompL2]
    #creation du dictionnaire
    for i in range(len(CL2)):
        dict[i] = []
        for conc in CL2:
            if set(CL2[i].c).issubset(conc.c) and not set(conc.c).issubset(CL2[i].c):
                dict[i].append(conc)
    #Calcul des classes d'équivalences
    Indices = sorted(zip(CL2,range(len(CL2))), key=lambda pair: pair[0].c)
    end = 0
    while end == 0:
        end = 1
        for i in Indices:
            if CL2[i[1]].b == 0:
                aTraiter = 1
                sum = 0
                for conc2 in dict[i[1]]:
                    if conc2.b == 0:
                        aTraiter = 0
                        break
                    sum += conc2.t
                if aTraiter == 1 and (len(CL2[i[1]].c) > 0 or len(CL2) == 1):
                    end = 0
                    CL2[i[1]].t = pow(2,(nbAtt-len(CL2[i[1]].c)))-sum
                    classe_max_L2 += CL2[i[1]].t
                    CL2[i[1]].b = 1

    if classe_max_L1 > 0 or classe_max_L2 > 0:
        nb1 = classe_max_L1
        nb2 = classe_max_L2
        nb12 = classe_max_intersection
        Res = pow(pow(abs(nb1-nb12),q)+pow(abs(nb2-nb12),q),1.0/q)
        Res = Res/(nb12+pow(pow(abs(nb1-nb12),q)+pow(abs(nb2-nb12),q),1.0/q))
        result.append(Res)
    else:
        result.append(0) 
