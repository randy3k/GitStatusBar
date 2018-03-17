import sublime
import sublime_plugin
import subprocess
import os
import re


def plugin_loaded():
    s = sublime.load_settings("Git.sublime-settings")
    if s.get("statusbar_branch"):
        s.set("statusbar_branch", False)
        sublime.save_settings("Git.sublime-settings")
    if s.get("statusbar_status"):
        s.set("statusbar_status", False)
        sublime.save_settings("Git.sublime-settings")
    ofile = os.path.join(sublime.packages_path(), "User", "Git-StatusBar.sublime-settings")
    nfile = os.path.join(sublime.packages_path(), "User", "GitStatusBar.sublime-settings")
    if os.path.exists(ofile):
        os.rename(ofile, nfile)


def plugin_unloaded():
    """reset sublime-text-git status bar"""
    s = sublime.load_settings("Git.sublime-settings")
    if s.get("statusbar_branch") is False:
        s.set("statusbar_branch", True)
        sublime.save_settings("Git.sublime-settings")
    if s.get("statusbar_status") is False:
        s.set("statusbar_status", True)
        sublime.save_settings("Git.sublime-settings")


class GitManager:
    def __init__(self, view):
        self.view = view
        s = sublime.load_settings("GitStatusBar.sublime-settings")
        self.git = s.get("git", "git")
        self.prefix = s.get("prefix", "")

    def run_git(self, cmd, cwd=None):
        plat = sublime.platform()
        if not cwd:
            cwd = self.getcwd()
        if cwd:
            if type(cmd) == str:
                cmd = [cmd]
            cmd = [self.git] + cmd
            if plat == "windows":
                # make sure console does not come up
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     cwd=cwd, startupinfo=startupinfo)
            else:
                my_env = os.environ.copy()
                my_env["PATH"] = "/usr/local/bin:/usr/bin:" + my_env["PATH"]
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     cwd=cwd, env=my_env)
            p.wait()
            stdoutdata, _ = p.communicate()
            return stdoutdata.decode('utf-8')

    def getcwd(self):
        f = self.view.file_name()
        cwd = None
        if f:
            cwd = os.path.dirname(f)
        if not cwd:
            window = self.view.window()
            if window:
                pd = window.project_data()
                if pd:
                    cwd = pd.get("folders")[0].get("path")
        return cwd

    def branch(self):
        ret = self.run_git(["symbolic-ref", "HEAD", "--short"])
        if ret:
            ret = ret.strip()
        else:
            output = self.run_git("branch")
            if output:
                m = re.search(r"\* *\(detached from (.*?)\)", output, flags=re.MULTILINE)
                if m:
                    ret = m.group(1)
        return ret

    def is_dirty(self):
        output = self.run_git("status")
        if not output:
            return False
        ret = re.search(r"working (tree|directory) clean", output)
        if ret:
            return False
        else:
            return True

    def unpushed_info(self):
        branch = self.branch()
        a, b = 0, 0
        if branch:
            output = self.run_git(["branch", "-v"])
            if output:
                m = re.search(r"\* .*?\[behind ([0-9])+\]", output, flags=re.MULTILINE)
                if m:
                    a = int(m.group(1))
                m = re.search(r"\* .*?\[ahead ([0-9])+\]", output, flags=re.MULTILINE)
                if m:
                    b = int(m.group(1))
        return (a, b)

    def badge(self):
        branch = self.branch()
        if not branch:
            return ""
        ret = branch
        if self.is_dirty():
            ret = ret + "*"
        a, b = self.unpushed_info()
        if a:
            ret = ret + "-%d" % a
        if b:
            ret = ret + "+%d" % b
        return self.prefix + ret


class GitStatusBarHandler(sublime_plugin.EventListener):
    def update_status_bar(self, view):
        sublime.set_timeout_async(lambda: self._update_status_bar(view))

    def _update_status_bar(self, view):
        if not view or view.is_scratch() or view.settings().get('is_widget'):
            return
        gm = GitManager(view)
        badge = gm.badge()
        if badge:
            view.set_status("git-statusbar", badge)
        else:
            view.erase_status("git-statusbar")

    def on_new(self, view):
        self.update_status_bar(view)

    def on_load(self, view):
        self.update_status_bar(view)

    def on_activated(self, view):
        self.update_status_bar(view)

    def on_deactivated(self, view):
        self.update_status_bar(view)

    def on_post_save(self, view):
        self.update_status_bar(view)

    def on_pre_close(self, view):
        self.update_status_bar(view)

    def on_window_command(self, window, command_name, args):
        if command_name == "hide_panel":
            self.update_status_bar(window.active_view())
