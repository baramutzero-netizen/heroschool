local s=app.open('D:/heroschool/assets/battle-fields/areatournament/portrait-deskfix-source.png')
app.command.SpriteSize{ui=false,width=1080,height=1920,method='bilinear'}
s:saveCopyAs('D:/heroschool/assets/battle-fields/areatournament/portrait-deskfix.png')
s:close()