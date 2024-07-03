from abc import ABC, abstractmethod, abstractproperty

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n\t ##### Falha na operação! Saldo Insuficiente. ####")
            return False

        elif valor > 0:
            self._saldo -= valor
            print("\n ===== Saque efetuado com sucesso! =====")
            return True

        else:
            print("\n\t #### FALHA NA OPERAÇÃO! VALOR INFORMADO INVÁLIDO! ####")
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n\t ===== Depósito realizado com sucesso! =====")
            return True
        else:
            print("\n\t #### Falha no depósito! Valor informado inválido! ####")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=1000, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("\n #### Falha na operação! Valor de saque excedido. ####")
            return False

        elif excedeu_saques:
            print("\n  #### Falha na operação! Número de saques excedido. ####")
            return False

        else:
            return super().sacar(valor)

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor) -> None:
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """
            Bem vindo ao Banco Novo:

    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Nova Conta
    [5] Listar as Contas
    [6] Novo Usuário
    [0] Sair

    => """
    return input(menu)


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n #### Cliente não possui conta! ####")
        return None
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n #### Cliente não encontrado! ####")
        return

    valor = float(input("Informe o valor do depósito: "))

    if valor <= 0:
        print("\n\t #### FALHA NA OPERAÇÃO! VALOR DEPÓSITO INVÁLIDO! ####")
        return

    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n #### Cliente não encontrado! ####")
        return

    valor = float(input("Informe o valor de saque: "))

    if valor <= 0:
        print("\n\t #### FALHA NA OPERAÇÃO! VALOR DE SAQUE INVÁLIDO! ####")
        return

    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n #### Cliente não encontrado! ####")
        return

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    print("\n\t ================ EXTRATO ===============")
    transacoes = conta.historico.transacoes

    if not transacoes:
        print("Não foram realizadas movimentações em sua conta.")
    else:
        for transacao in transacoes:
            print(f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}")

    print(f"\nSaldo:\t R$ {conta.saldo:.2f}")
    print("\t =========================================\n\n")


def criar_cliente(clientes):
    cpf = input("Informe o seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n#### Já existe cliente com esse CPF! ####")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa)")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n ===== Cliente criado com sucesso! =====")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas, clientes):
    cpf = input("Informe o CPF do cliente para filtrar as contas (deixe em branco para listar todas): ")

    if cpf:
        cliente = filtrar_cliente(cpf, clientes)
        if not cliente:
            print("\n#### Cliente não encontrado! ####")
            return

        contas_cliente = [conta for conta in contas if conta.cliente == cliente]

        if not contas_cliente:
            print(f"\n#### Cliente {cliente.nome} não possui contas cadastradas. ####")
        else:
            for conta in contas_cliente:
                print("=" * 100)
                print(f"Agência: {conta.agencia}")
                print(f"Conta: {conta.numero}")
                print(f"Titular: {conta.cliente.nome}")
                print(f"CPF do Titular: {conta.cliente.cpf}")
                print(f"Saldo: R$ {conta.saldo:.2f}")
                print("=" * 100)
    else:
        print("\n#### Dados restritos! Informe o CPF para listar as contas de um cliente. ####")

        if not contas:
            print("\n#### Nenhuma conta cadastrada! ####")
        else:
            for conta in contas:
                print("=" * 100)
                print(f"Agência: {conta.agencia}")
                print(f"Conta: {conta.numero}")
                print(f"Titular: {conta.cliente.nome}")
                print(f"CPF do Titular: {conta.cliente.cpf}")
                print(f"Saldo: R$ {conta.saldo:.2f}")
                print("=" * 100)


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "6":
            criar_cliente(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            listar_contas(contas, clientes)

        elif opcao == "0":
            confirmacao = input("\nTem certeza que deseja sair? (S/N): ").strip().lower()
            if confirmacao == 's':
                break

        else:
            print("### Operação inválida, por favor selecione novamente a operação desejada. ###")


if __name__ == "__main__":
    main()
