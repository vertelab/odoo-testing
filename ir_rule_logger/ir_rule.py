from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class Model(models.Model):
    def _apply_ir_rules(self, cr, uid, query, mode='read', context=None):
        """Add what's missing in ``query`` to implement all appropriate ir.rules
          (using the ``model_name``'s rules or the current model's rules if ``model_name`` is None)

           :param query: the current query object
        """
        if uid == SUPERUSER_ID:
            return

        def apply_rule(added_clause, added_params, added_tables, parent_model=None):
            """ :param parent_model: name of the parent model, if the added
                    clause comes from a parent model
            """
            _logger.warn('apply rule\nadded_clause: %s\nadded_params: %s\nadded_tables: %s\nparent_model: %s' % (added_clause, added_params, added_tables, parent_model))
            if added_clause:
                if parent_model:
                    # as inherited rules are being applied, we need to add the missing JOIN
                    # to reach the parent table (if it was not JOINed yet in the query)
                    parent_alias = self._inherits_join_add(self, parent_model, query)
                    # inherited rules are applied on the external table -> need to get the alias and replace
                    parent_table = self.pool[parent_model]._table
                    added_clause = [clause.replace('"%s"' % parent_table, '"%s"' % parent_alias) for clause in added_clause]
                    # change references to parent_table to parent_alias, because we now use the alias to refer to the table
                    new_tables = []
                    for table in added_tables:
                        # table is just a table name -> switch to the full alias
                        if table == '"%s"' % parent_table:
                            new_tables.append('"%s" as "%s"' % (parent_table, parent_alias))
                        # table is already a full statement -> replace reference to the table to its alias, is correct with the way aliases are generated
                        else:
                            new_tables.append(table.replace('"%s"' % parent_table, '"%s"' % parent_alias))
                    added_tables = new_tables
                query.where_clause += added_clause
                query.where_clause_params += added_params
                for table in added_tables:
                    if table not in query.tables:
                        query.tables.append(table)
                _logger.warn('True')
                return True
            _logger.warn('False')
            return False

        # apply main rules on the object
        rule_obj = self.pool.get('ir.rule')
        rule_where_clause, rule_where_clause_params, rule_tables = rule_obj.domain_get(cr, uid, self._name, mode, context=context)
        apply_rule(rule_where_clause, rule_where_clause_params, rule_tables)

        # apply ir.rules from the parents (through _inherits)
        for inherited_model in self._inherits:
            rule_where_clause, rule_where_clause_params, rule_tables = rule_obj.domain_get(cr, uid, inherited_model, mode, context=context)
            apply_rule(rule_where_clause, rule_where_clause_params, rule_tables,
                       parent_model=inherited_model)




"""
class ir_rule(models.Model):
    _inherit = 'ir.rule'

    def _eval_context_for_combinations(self):
        res = super(ir_rule, self)._eval_context_for_combinations()
        _logger.warn('_eval_context_for_combinations returned: %s' % res)
        return res

    def _eval_context(self, cr, uid):
        res = super(ir_rule, self)._eval_context(cr, uid)
        _logger.warn('_eval_context returned: %s' % res)
        return res

    def _domain_force_get(self, cr, uid, ids, field_name, arg, context=None):
        res = super(ir_rule, self)._domain_force_get(cr, uid, ids, field_name, arg, context)
        _logger.warn('_domain_force_get\nids: %s\nfield_name: %s\narg:%s\nreturned: %s' % (ids, field_name, arg, res))
        return res

    def _get_value(self, cr, uid, ids, field_name, arg, context=None):
        res = super(ir_rule, self)._get_value(cr, uid, ids, field_name, arg, context)
        _logger.warn('_eval_context\nids: %s\nfield_name: %s\narg:%s\nreturned: %s' % (ids, field_name, arg, res))
        return res

    def _check_model_obj(self, cr, uid, ids, context=None):
        res = super(ir_rule, self)._check_model_obj(cr, uid, ids, context)
        _logger.warn('_check_model_obj\nids: %s\nreturned: %s' % (ids, res))
        return res
    
    def _check_model_name(self, cr, uid, ids, context=None):
        res = super(ir_rule, self)._check_model_name(cr, uid, ids, context)
        _logger.warn('_check_model_name\nids: %s\nreturned: %s' % (ids, res))
        return res    
    
    def domain_get(self, cr, uid, model_name, mode='read', context=None):
        res = super(ir_rule, self).domain_get(cr, uid, model_name, mode, context)
        _logger.warn('domain_get\nmodel_name: %s\nmode:%s\nreturned: %s' % (model_name, mode, res))
        return res
    
   
    @tools.ormcache()
    def _compute_domain(self, cr, uid, model_name, mode="read"):
        
        return []

    def clear_cache(self, cr, uid):
        self._compute_domain.clear_cache(self)
    """
        
