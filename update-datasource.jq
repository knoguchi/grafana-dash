#!/usr/bin/env -S jq -Mf

walk(
  if type == "object" and has("datasource") then
    if .datasource == $old then
      .datasource = $new
    else
     .
    end
  elif type == "object" and has("current") then
    if .current.text == $old and .current.value == $old then
      .current.text = $new | .current.value = $new
    else
      .
    end
  else
    .
  end
)
