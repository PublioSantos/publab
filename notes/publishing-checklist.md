# Checklist antes do primeiro push

Nada publicado até aqui. Decidido em revisão (03/10/2026):

## Decidido

- **Repositório:** `github.com/PublioSantos/publab`
  (não `kofplab` — o produto é PubLab; ser implementado em Kof não precisa
  aparecer no nome do repositório).
- **Atribuição:** `Powered by: Kof` vive em um único módulo de branding,
  `publab/app/Brand.kf`, e a UI consome de lá. A string não é repetida no
  código. Coberto por `tests/brand_test.kf`.
- **README:** diz `Powered by: Kof` com link, status por fase, e o aviso de
  modelo educacional do 8051/Cortex-M3 em EN e PT.

## Pendente

- [x] **LICENSE: MIT.** Decidido em 04/10/2026. Arquivo `LICENSE` na raiz,
      copyright "2026 Publio Santos". O Kof ser GPLv3 não decide a licença do
      PubLab — o PubLab usa a toolchain, não vendoriza o compilador.
- [x] **Link do `Powered by: Kof`: `https://github.com/KofLang/Kof4j`.**
      Decidido em 04/10/2026 — o repositório, não o site. Vive só em
      `publab/app/Brand.kf`.
- [ ] Autorização explícita para publicar.
