from spark import GenericASTTraversal
from automator import Automator


class ExecuteCommands(GenericASTTraversal):
    def __init__(self, ast, real=True):
        GenericASTTraversal.__init__(self, ast)
        self.output = []
        self.automator = Automator(real)

        self.postorder()

    def EC_exec(self):
        return self.automator.flush()
##############

    def n_num(self, node):
        self.automator.key(str(node.meta[0]))

##############
    def n_modifier(self, node):
        self.automator.modifier(node.meta[0])

    def n_modified(self, node):
        self.automator.modified(node.meta[0])


    def n_char(self, node):
        self.automator.key(node.meta[0])

    def n_raw_char(self, node):
        self.automator.raw_key(node.meta[0])

    def n_movement(self, node):
        self.automator.key(node.meta[0])

    def n_sequence(self, node):
        for c in node.meta[0]:
            self.automator.raw_key(c)

    def n_word_sequence(self, node):
        n = len(node.children)
        for i in range(0, n):
            word = node.children[i].meta
            for c in word:
                self.automator.raw_key(c)
            if (i + 1 < n):
                self.automator.raw_key('space')

    def n_null(self, node):
        pass

    def n_repeat(self, node):
        # print(node.children)
        xdo = self.automator.xdo_list[-1]
        for n in range(1, node.meta[0].meta[0]):
            self.automator.xdo(xdo)

    def default(self, node):
        #        for child in node.children:
        #            self.automator.execute(child.command)
        pass


def execute(ast, real):
    EC = ExecuteCommands(ast, real)
    command = EC.EC_exec()
    return command
