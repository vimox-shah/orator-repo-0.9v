# -*- coding: utf-8 -*-

from flexmock import flexmock, flexmock_teardown
from orator.orm.scopes import SoftDeletingScope
from orator.orm import Builder, Model
from orator.query import QueryBuilder
from ... import OratorTestCase, mock


class SoftDeletingScopeTestCase(OratorTestCase):

    def tearDown(self):
        flexmock_teardown()

    def test_apply_scope_to_a_builder(self):
        scope = SoftDeletingScope()
        query = flexmock(QueryBuilder(None, None, None))
        builder = Builder(query)
        model = flexmock(ModelStub())
        model.should_receive('get_qualified_deleted_at_column').once().and_return('table.deleted_at')
        builder.get_query().should_receive('where_null').once().with_args('table.deleted_at')

        scope.apply(builder, model)

    def test_force_delete_extension(self):
        scope = SoftDeletingScope()
        builder = Builder(None)
        scope.extend(builder)
        callback = builder.get_macro('force_delete')
        query = flexmock(QueryBuilder(None, None, None))
        given_builder = Builder(query)
        query.should_receive('delete').once()

        callback(given_builder)

    def test_restore_extension(self):
        scope = SoftDeletingScope()
        builder = Builder(None)
        scope.extend(builder)
        callback = builder.get_macro('restore')
        query = flexmock(QueryBuilder(None, None, None))
        builder_mock = flexmock(BuilderWithTrashedStub)
        given_builder = BuilderWithTrashedStub(query)
        builder_mock.should_receive('with_trashed').once()
        builder_mock.should_receive('get_model').once().and_return(ModelStub())
        builder_mock.should_receive('update').once().with_args({'deleted_at': None})

        callback(given_builder)

    def test_with_trashed_extension(self):
        scope = flexmock(SoftDeletingScope())
        builder = Builder(None)
        scope.extend(builder)
        callback = builder.get_macro('with_trashed')
        query = flexmock(QueryBuilder(None, None, None))
        given_builder = Builder(query)
        model = flexmock(ModelStub())
        given_builder.set_model(model)

        given_builder.remove_global_scope = mock.MagicMock(return_value=given_builder)
        result = callback(given_builder)

        self.assertEqual(given_builder, result)
        given_builder.remove_global_scope.assert_called_with(scope)


class ModelStub(Model):

    def get_qualified_deleted_at_column(self):
        return 'table.deleted_at'

    def get_deleted_at_column(self):
        return 'deleted_at'


class BuilderWithTrashedStub(Builder):

    def with_trashed(self):
        pass
