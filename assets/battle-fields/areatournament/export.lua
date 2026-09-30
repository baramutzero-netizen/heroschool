local root='D:/heroschool/assets/battle-fields/areatournament/'
for _,v in ipairs({{'portrait',1080,1920},{'landscape',1920,960}}) do
 local s=app.open(root..v[1]..'-source.png')
 app.command.SpriteSize{ui=false,width=v[2],height=v[3],method='bilinear'}
 s:saveCopyAs(root..v[1]..'.png');s:close()
end
