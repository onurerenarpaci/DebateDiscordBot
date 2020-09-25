team_name= "Koç Allahuekber Dağları".split(" ")
user_name= "Taylan Alpkaya".split(" ")
name = ""
team = ""
teams_turn = True
i,j = 0,0
total_lenght = 1

while total_lenght < 28:
    if teams_turn and i < len(team_name):
        total_lenght += (len(team_name[i])+1)
        i += 1
        teams_turn = False
    elif j < len(user_name):
        total_lenght += (len(user_name[j])+1)
        j += 1
        teams_turn = True
    elif teams_turn == False and j == len(user_name):
        teams_turn = True
    if j == len(user_name) and i == len(team_name):
        break
        
team = " ".join(team_name[0:i])
name = " ".join(user_name[0:j])
if total_lenght > 32:
    dif = total_lenght - 32
    if len(team) > 15:
        team = team[0:-dif]
    else:
        name = name[0:-dif]
final = team + " - " + name
print(final)
print(len(final))