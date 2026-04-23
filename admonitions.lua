-- admonitions.lua
-- Convierte !!! tip/warning "Título"\n    contenido
-- a párrafo con negrita para el PDF generado por pandoc

function Para(el)
  local text = pandoc.utils.stringify(el)

  local atype, title, rest = text:match('^!!!%s+(%a+)%s+"([^"]*)"(.*)$')
  if not atype then
    atype, title = text:match('^!!!%s+(%a+)%s+(.-)%s*$')
    rest = ''
  end
  if not atype then return nil end

  local content = (rest or ''):gsub('^%s+', ''):gsub('%s+$', '')
  local prefix  = (atype == 'warning') and '[!] ' or '[>] '

  -- Construir inlines: [Strong(prefix+title), Str(" — "), ...contenido...]
  local inlines = pandoc.List()
  inlines:insert(pandoc.Strong({ pandoc.Str(prefix .. title) }))

  if content ~= '' then
    inlines:insert(pandoc.Str(' \u{2014} '))   -- em dash
    local parsed = pandoc.read(content, 'markdown')
    if parsed.blocks[1] and parsed.blocks[1].t == 'Para' then
      inlines:extend(parsed.blocks[1].content)
    else
      inlines:insert(pandoc.Str(content))
    end
  end

  return pandoc.Para(inlines)
end
