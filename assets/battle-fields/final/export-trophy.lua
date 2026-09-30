local s=app.open('D:/heroschool/assets/battle-fields/final/landscape-trophy-source.png')
app.command.SpriteSize{ui=false,width=1920,height=960,method='bilinear'}
s:saveCopyAs('D:/heroschool/assets/battle-fields/final/landscape-trophy.png')
s:close()
