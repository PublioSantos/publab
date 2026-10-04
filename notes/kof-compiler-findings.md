# Achados do compilador Kof durante o PubLab

Notas locais. **Nada aqui foi reportado como issue** — registro para decidir
depois se entra no fluxo do `kofbughunter`, com repro mínimo próprio e
seguindo o template de issue.

Toolchain: `kof-toolchain/current` → `kof-beta-tip`, VERSION `0.5.0-beta`.
Target usado: `jvm`.

---

## 1. `List<T>` de record local do pacote não aceita anotação vazia (SEM010)

Dentro do **mesmo pacote** onde o `record` é declarado, anotar um local como
`List<Record>` e atribuir `listOf()` é rejeitado, enquanto o tipo de retorno da
mesma função é aceito:

```kof
package publab.machine

record OpSpec(Int opcode, String mnemonic, Int form)

List<OpSpec> opcodeTable() {
    var table: List<OpSpec> = listOf()    // SEM010
    return table
}
```

```
Opcodes.kf:51:5: error: Return type mismatch:
  expected 'List<publab.machine.OpSpec>' but got 'List<OpSpec>' [SEM010]
```

O tipo de **retorno** `List<OpSpec>` é qualificado para
`List<publab.machine.OpSpec>`; o tipo **declarado do local** não é, e os dois
não unificam. Erro em tempo de compilação, não silencioso.

Dois workarounds, ambos usados no projeto:

```kof
var table = listOf(OpSpec(0x00, "HALT", formNone()))     // semear e inferir
var l: List<publab.machine.OpSpec> = listOf()            // qualificar à mão
```

Os helpers `emptyDiagnostics()`, `emptyTokens()`, `emptyOperands()`,
`emptyInstructions()`, `emptyLabels()`, `emptyPlaced()`, `emptySymbols()` e
`emptySourceMap()` existem por causa disto — isolam a forma qualificada em uma
linha por tipo.

**Antes de abrir qualquer coisa:** conferir `grammar.md` e `DECISIONS.md`
(regra de qualificação de nomes simples, `qualifyDeep`/`CompilerTypes`) para
saber se isso é comportamento decidido e não um bug.

---

## 2. `kof check <dir>` não enxerga subdiretórios

`kof check .` na raiz do projeto responde `no .kf/.kof files found`, e
`kof check publab/machine` falha com `PKG004` porque trata o diretório passado
como module root:

```
publab/machine/Alu.kf:0:0: error: package 'publab.machine' does not match
  the directory ('') — a directory is a package [PKG004]
```

Consequência prática: **não existe passo de type-check do projeto inteiro**. O
type-check acontece via `kof test tests`, porque cada arquivo de teste importa
os pacotes e o compilador expande o diretório. Não é bug confirmado — pode ser
só a superfície do CLI.

---

## 3. Confirmados funcionando (sem surpresa, mas foram probados antes de usar)

Probados no 0.5.0-beta/jvm antes de escrever a máquina, para não construir
sobre suposição:

- bitwise `& | ^ << >> >>>` em `Long`, incluindo máscaras de 8/16/32 bits
- `4294967295 as Long` (não existe literal long)
- `Char` com `>=`/`<=`, escapes `'\n'`/`'\t'`, `c as Int`
- `else if` em cadeia
- `new Long[n]` / `new Int[n]` como campo de classe
- `record` com campo `List<T>`; `enum` em campo de classe
- `try`/`catch (String e)` com `throw "msg"` em função própria
- `String.toUpperCase/indexOf/trim/compareTo/substring(a)/charAt`
- import cross-diretório com `kof.toml` na raiz como module root
- `kof test` por arquivo: vários arquivos de teste no mesmo diretório sem
  colidir em `PKG002`, e sem precisar de `main()`
- leitura de arquivo relativa ao cwd dentro de `kof test` (`File(p).readText()`)
