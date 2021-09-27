import os
import cProfile as profile
from lex import VerilogLexerPlex as VerilogLexer
from par_lalr import VerilogParser


if __name__ == '__main__':
    lex = VerilogLexer(error_func=lambda s: print(s))

    with open(os.path.join(__file__, '../verilog_example_1.v')) as fd:
        lex.input(fd.read())
    # lex.input('''
    # module top;
    # reg count;
    # always @* begin
    #     if (1) count = 1;
    #     else count = 0;
    # end
    # endmodule
    # ''')

    pr = profile.Profile()
    pr.enable()
    tokens = []
    for t in lex:
        tokens.append(t)
    pr.disable()
    pr.print_stats()
    # print(f'====== tokens ({len(tokens)}) ======')
    # print(tokens)

    par = VerilogParser(debug=True)
    # par.grammar.print_analysis_table()
    # print(par.grammar.stringify_item_collection(par.grammar._itemcol[213]))
    # print(par.grammar.stringify_item_collection(par.grammar._itemcol[232]))

    pr = profile.Profile()
    pr.enable()
    astroot = par.parse(iter(tokens))
    pr.disable()
    pr.print_stats()

    astroot.show()

