'use client'

import * as React from "react"
import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { Calendar as CalendarIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function DatePicker({ value, onChange, placeholder = "Выберите дату", disabled = false, className, name }) {
  const [date, setDate] = React.useState(value ? new Date(value) : null)

  React.useEffect(() => {
    if (value) {
      const parsedDate = new Date(value)
      if (!isNaN(parsedDate.getTime())) {
        setDate(parsedDate)
      } else {
        setDate(null)
      }
    } else {
      setDate(null)
    }
  }, [value])

  const handleSelect = (selectedDate) => {
    setDate(selectedDate)
    if (onChange) {
      // Форматируем дату в формат YYYY-MM-DD для input
      const formattedDate = selectedDate ? format(selectedDate, 'yyyy-MM-dd') : ''
      // Создаем событие с правильным name, если оно передано
      const event = { 
        target: { 
          value: formattedDate,
          name: name || 'date'
        } 
      }
      onChange(event)
    }
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "w-full justify-start text-left font-normal",
            !date && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "dd.MM.yyyy", { locale: ru }) : <span>{placeholder}</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={date}
          onSelect={handleSelect}
          initialFocus
          locale={ru}
        />
      </PopoverContent>
    </Popover>
  )
}

