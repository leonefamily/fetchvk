# fetchvk

![image](https://user-images.githubusercontent.com/77976599/156900282-1f38145c-2d07-490a-8b13-2e71bbee8372.png)

Download your data from VKontakte servers in order to keep all your photos and messages even after you delete your account.
Currently only supports downloading of photos from albums without metadata, more features to come in the future.
Tested on Windows 10 and Raspberry Pi OS (Linux Debian) with Python 3.7.9 and 3.9.1, will potentially work on all platforms.

...

Загрузите свои данные с серверов ВКонтакте, чтобы даже после удаления профиля иметь доступ к своим фотографиям и сообщениям.
На данный момент поддерживается только загрузка фотографий (без метаданных - даты и места) из альбомов, другие функции появятся позже.
Проверено на Windows 10 и Raspberry Pi OS (Linux Debian) с версиями Python 3.7.9 и 3.9.1, но работать должно на всех платформах.

## How to install / Как установить
You need to have Python 3 installed with pip (installed by default with Python). Download and extract the archive from this repository:



Inside the directory with the unpacked archive call the command prompt (on Windows - hold Shift + RMB, "Open PowerShell here", on Linux or MacOS - if you have Linux, you know how to use the Terminal :laughing:), enter:
```
python3 setup.py install
```
The required dependencies should be installed now. After that, the command prompt can be closed.

...

Необходимо иметь установленный Python 3 с утилитой pip (устанавливается по умолчанию вместе с Python). Скачайте и распакуйте архив из этого репозитория, внутри директории с распакованным архивом вызовите командную строку (на Windows - удерживать Shift + ПКМ, "Открыть здесь окно PowerShell", в Linux или MacOS - если у вас Линукс, вы знаете, как пользоваться терминалом :laughing:), введите:
```
python3 setup.py install
```
Необходимые зависимости должны будут установиться. После этого командную строку можно будет закрыть.

## How to use / Как использовать
Go to page https://vk.com/data_protection?section=rules, scroll down to button "Request Data Copy", enter your credentials and request an archive.
When done, double click "gui.py", enter path to the archive and to the folder you want to save data in. If the archive is already unpacked, check the checkbox "Archive is a folder" and enter path to unpacked archive location. If you'd like to see all text output from the script, keep "Verbose" checkbox checked, if unchecked, it will only show warnings and errors. If "Close when done" is checked, window will disappear after downloading is done.
Should you encounter any errors, don't hesitate to contact me.

...

Перейдите на страницу https://vk.com/data_protection?section=rules, прокрутите вниз до кнопки «Запросить архив», введите пароль к своему профилю и скачайте архив.

![image](https://user-images.githubusercontent.com/77976599/156900236-3a1b6061-7765-41ce-bb60-9c27882ee4ae.png)

После загрузки дважды щёлкните на "gui.py", введите путь к архиву и к папке, в которой вы хотите сохранить данные. Если архив уже распакован, установите флажок "Archive is a folder" и введите путь к месту расположения распакованного архива. Если вы хотите видеть весь текст, выводимый скриптом, выберите флажок "Verbose". Если он не выбран, будут отображаться только предупреждения и ошибки. Если выбран флажок "Close when done", окно исчезнет после завершения загрузки.
Если встретятся какие-либо ошибки, напишите мне.