# Шрифты OG-карточек

Оба шрифта под SIL Open Font License 1.1 — вшиты в репозиторий, чтобы карточка
рисовалась одинаково на macOS и на раннере GitHub Actions.

| Файл | Роль в шаблоне | Источник | Лицензия |
|---|---|---|---|
| `RussoOne-Regular.ttf` (v1.0) | заголовок-хук (`F_BLACK`) | [google/fonts · ofl/russoone](https://github.com/google/fonts/tree/main/ofl/russoone) | `OFL-RussoOne.txt` |
| `LiberationSans-Bold.ttf` (2.1.5) | бренд, акцент, подпись пресета | [liberationfonts](https://github.com/liberationfonts/liberation-fonts), пакет `fonts-liberation` 2.1.5-3 | `OFL-LiberationSans.txt` |
| `LiberationSans-Regular.ttf` (2.1.5) | футер | там же | `OFL-LiberationSans.txt` |

Почему не Arial/Arial Black: в CI их нет, и они не распространяются свободно.
Archivo Black, который подходил по тяжести, отпал — в нём нет кириллицы
(подмножества только latin/latin-ext), а хуки русские.

Оба выбранных шрифта покрывают кириллицу, «—», «·», «?», цифры и латиницу.
Перед заменой шрифта проверь покрытие, иначе текст хука превратится в «квадраты».
