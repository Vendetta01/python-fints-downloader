# TODO

* [ ] fints: get_scheduled_debits
* [ ] Add tests
* [ ] Write correct MT535-Parser: Collapsing of multilines are a bit more complicated because free text fields have line numbers in front of each line (except the first)
* [ ] Save client/dialog/tan data in db an "lock" accounts that are logged in for other connection attempts
* [ ] Test tan method with dkb (vblh get_transactions is currently not working, don't know why...)
* [ ] Refactor base_generic.html: put side bar into own template
* [ ] Split models.py into individual files
* [ ] Menu: sub menu entries should be indented
* [ ] Menu: sub menu with symbol collapsed/not collapsed (https://codepen.io/Paulie-D/pen/BoXgbj, https://www.codeply.com/go/ETdG3HL7sB)
* [ ] Category/categories endpoints: model as form to create/update/delete data sets
* [ ] Write categorizer that handles automatic assignment of categories to new transactions
* [ ] Admin command to trigger import
* [X] Implement template for categories
* [ ] Update model.plantuml (maybe automatically from code???)
* [X] Make target for model.plantuml
* [ ] Remove Balance
* [ ] Create Dockerfile
* [ ] Update accounts template (enable/disable foreign accounts)
