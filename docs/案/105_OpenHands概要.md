# OpenHands 概要

参照：https://github.com/All-Hands-AI/OpenHands

---

## OpenHandsとは

AIエージェントが実際にコードを書き、実行し、ファイルを操作し、Webを閲覧する**AI駆動型ソフトウェア開発プラットフォーム**。

「人間の開発者がやることをすべてAIに任せる」がコンセプト。コード生成にとどまらず、ターミナル操作・ブラウザ操作・ファイル管理まで実行できる点が特徴。

TikTok・Amazon・Netflix・Google・NVIDIAなど大手企業でも採用。

---

## できること

| 機能 | 内容 |
|---|---|
| コード生成・実行 | コードを書いてその場で実行・デバッグ |
| ファイル操作 | ファイルの作成・編集・削除 |
| ターミナル操作 | シェルコマンドの実行 |
| ブラウザ操作 | Web検索・ページ閲覧 |
| GitHub/GitLab連携 | PR作成・Issue対応の自動化 |
| Slack/Jira/Linear連携 | 外部ツールとの統合 |

---

## 基本構造

### エージェントの種類

| 種類 | 説明 |
|---|---|
| Software Agent SDK | コードで定義する構成可能なエージェント（ローカル〜クラウドスケール） |
| CLI Agent | ターミナルから使うエージェント（Claude・GPT等に対応） |
| GUI Agent | ローカルGUI（React）でビジュアル操作 |
| Cloud Agent | OpenHands Cloudでホスト型実行 |
| Enterprise Agent | VPC内自己ホスト・Kubernetes対応 |

### アーキテクチャ

```
ユーザー（自然言語で指示）
  └─▶ エージェントコア（Python SDK）
        ├─▶ コード実行（Dockerサンドボックス）
        ├─▶ ファイル操作
        ├─▶ ターミナル操作
        └─▶ ブラウザ操作
```

- **サンドボックス**：Dockerコンテナで安全に実行
- **インターフェース**：CLI / REST API / React GUI
- **LLM**：Claude・GPT・その他に対応

---

## 使用技術

| 項目 | 内容 |
|---|---|
| バックエンド | Python SDK |
| フロントエンド | React（SPA） |
| 実行環境 | Docker / Kubernetes |
| API | REST API |
| ライセンス | MIT（エンタープライズ部分を除く） |

---

## 本プロジェクトとの関連

OpenHandsの「エージェントが実際に手を動かして実行する」仕組みは、本プロジェクトの**製造工程管理部門・製造工程分解部門**の実装参考になる。特にDockerサンドボックスによる安全な実行環境の設計は応用できる。
