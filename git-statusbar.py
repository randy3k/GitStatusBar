import sublime
import sublime_plugin
import subprocess
import os
import re


class GitManager:
    def __init__(self, view):
        self.view = view

    def run_git_command(self, cmd, cwd=None):
        if not cwd:
            cwd = self.getcwd()
        if cwd:
            cmd = ["/usr/local/bin/git"] + cmd
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)
            p.wait()
            stdoutdata, _ = p.communicate()
            return stdoutdata.decode('utf-8')

    def getcwd(self):
        cwd = os.path.dirname(self.view.file_name())
        if not cwd:
            pd = self.view.window().project_data()
            if pd:
                cwd = pd.get("folders")[0].get("path")
        return cwd

    def branch(self):
        ret = self.run_git_command(["symbolic-ref", "HEAD", "--short"]).strip()
        if not ret:
            output = self.run_git_command(["branch"])
            if output:
                m = re.search(r"\* *\(detached from (.*?)\)", output, flags=re.MULTILINE)
                ret = m.group(1)
        return ret

    def is_dirty(self):
        output = self.run_git_command(["status"])
        ret = "working directory clean" not in output
        return ret

    def unpushed_info(self):
        branch = self.branch()
        a, b = 0, 0
        if branch:
            output = self.run_git_command(["branch", "-v"])
            if output:
                m = re.search(r"\* .*?\[ahead ([0-9])+\]", output, flags=re.MULTILINE)
                if m:
                    a = int(m.group(1))
                m = re.search(r"\* .*?\[behind ([0-9])+\]", output, flags=re.MULTILINE)
                if m:
                    b = int(m.group(1))
        return (a, b)

    def formatted_branch(self):
        branch = self.branch()
        ret = None
        if branch:
            ret = branch
            if self.is_dirty():
                ret = ret + "*"
            a, b = self.unpushed_info()
            if a:
                ret = ret + "+%d" % a
            if b:
                ret = ret + "-%d" % b
            ret = "(%s)" % ret
        return ret


class GitStatusBarHandler(sublime_plugin.EventListener):
    def on_activated(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return
        view.erase_status("git-statusbar")
        gm = GitManager(view)
        branch = gm.branch()
        if branch:
            view.set_status("git-statusbar", gm.formatted_branch())
