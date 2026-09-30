for _,k in ipairs({'citytournament','areatournament'}) do
 local root='D:/heroschool/assets/battle-fields/'..k..'/'
 local s=app.open(root..'portrait-props-source.png')
 app.command.SpriteSize{ui=false,width=1080,height=1920,method='bilinear'}
 s:saveCopyAs(root..'portrait-props.png');s:close()
end
