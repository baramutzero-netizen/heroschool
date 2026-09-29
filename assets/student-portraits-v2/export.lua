local jobs={'paladin','sword','monk','druid','archer','rogue','wizard','forcemage','spellsword','gunner','ninja','priest','darkpriest','timemage','enchanter','bard'}
local root='D:/heroschool/assets/student-portraits-v2/'
for _,job in ipairs(jobs) do
 local s=app.open(root..job..'.png')
 app.command.SpriteSize{ui=false,width=512,height=512,method='bilinear'}
 s:saveCopyAs(root..job..'-512.png')
 s:close()
end
