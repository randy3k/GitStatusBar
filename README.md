Git-StatusBar: A more compact Git StatusBar
====

[sublime-text-git](https://github.com/kemayo/sublime-text-git) does an amazing job in integrating `git` commands into Sublime Text. However, it is showing too much text in the status bar. This plugin minimizes the amount of text by only showing important information. Less is more!

### Screenshot

![](https://raw.githubusercontent.com/randy3k/Git-StatusBar/master/screenshot.png)

### Explain the badge

| symbol |                                                          |
| ----   | ----                                                     |
| *      | the current branch is dirty                              |
| +n     | the current branch is n commits ahead the remote branch  |
| -n     | the current branch is n commits behind the remote branch |

### Note
You can disable the `sublime-text-git` status bar by adding the following settings in `Git.sublime-settings`

```
{
    "statusbar_branch": false,
    "statusbar_status": false
}
```